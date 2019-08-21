from __future__ import print_function
import influxdb
import sys

migrate_query_template = ('SELECT * INTO "{target_db}"..:MEASUREMENT'
                          ' FROM "{measurement}"'
                          ' WHERE _tenant_id=\'{tenant_id}\''
                          ' AND time > {lower_time_offset}'
                          ' AND time <= {upper_time_offset}'
                          ' GROUP BY *')

two_weeks = dict(name='2w', duration='2w', replication='1', default=True)

class MigrationHelper(object):

    def __init__(self, source_db, host, verbosity=1):
        self.client = influxdb.InfluxDBClient(host=host, database=source_db)
        self.verbosity = verbosity

    def _migrate(self, measurement, tenant_id,
                 start_time_offset, end_time_offset,
                 target_db='target', retention_policy={},
                 time_offset_template='now()-{}w',
                 db_per_tenant=True, **kwargs):

        total_written = 0
        first_upper_time_offset = None
        upper_time_offset = None
        lower_time_offset = None
        time_offset = start_time_offset

        if db_per_tenant:
            target_db = "{}_{}".format(target_db, tenant_id)
        self.client.create_database(target_db)
        if retention_policy:
            self.client.create_retention_policy(database=target_db, **retention_policy)
        print('         into {}:'.format(target_db))

        while end_time_offset > 0 and time_offset < end_time_offset:
            lower_time_offset = time_offset_template.format(time_offset + 1)
            upper_time_offset = time_offset_template.format(time_offset)
            if not first_upper_time_offset:
                first_upper_time_offset = upper_time_offset
            migrate_query = migrate_query_template.format(
                target_db=target_db,
                measurement=measurement,
                tenant_id=tenant_id,
                lower_time_offset=lower_time_offset,
                upper_time_offset=upper_time_offset,
            )
            if (total_written == 0 and self.verbosity > 0) or self.verbosity > 1:
                print(migrate_query)

            written = next(self.client.query(migrate_query).get_points('result')).get('written')
            total_written += written
            time_offset += 1
            if written > 0:
                if (self.verbosity > 1 or (self.verbosity > 0 and time_offset % 10 == 0)):
                    print("         migrated {} entries from {} -> {} (cumulative {})".format(
                        written,
                        lower_time_offset,
                        upper_time_offset,
                        total_written,
                    ))
                else:
                    print(".", end="")
                    sys.stdout.flush()

        print("         finished migrating a total of {} entries from {} -> {}.".format(
            total_written,
            lower_time_offset,
            first_upper_time_offset,
        ))

    def get_measurements(self, fname):
        measurements = []
        if fname:
            with open(fname, 'a+') as f:
                measurements = [l.strip() for l in f.readlines()]
        if not measurements:
            measurements = [m.get('name') for m in self.client.query('SHOW MEASUREMENTS').get_points('measurements')]
            if fname:
                with open(fname, 'w') as f:
                    for r in measurements:
                        f.write(r + '\n')
        return measurements

    def get_tenancy(self, measurements):
        result = self.client.query("SHOW TAG VALUES WITH KEY = _tenant_id")
        return {m: [t.get('value') for t in result.get_points(m)] for m in measurements}

    def get_complete(self, fname):
        if fname:
            with open(fname, 'a+') as fd:
                return {l.strip() for l in fd.readlines()}
        else:
            return {}

    def migrate(self,
                project_defaults={},
                default_end_time_offset=52*5,
                default_start_time_offset=0,
                skip_functions=[lambda x: x.startswith('log.')],
                measurements_file=None, success_file=None, failure_file=None, **kwargs):
        measurements = self.get_measurements(measurements_file)
        tenancy = self.get_tenancy(measurements)
        done = self.get_complete(success_file)

        for i, measurement in enumerate(measurements):
            skip = any([f(measurement) for f in skip_functions])
            if measurement in done or skip:
                print('Skipping {} ({}/{})'.format(measurement, i+1, len(measurements)))
            else:
                print('Migrating {} ({}/{})'.format(measurement, i+1, len(measurements)))
                try:
                    for tenant_id in tenancy.get(measurement):
                        start_time_offset = project_defaults.get(tenant_id, {}).get('start', default_start_time_offset)
                        end_time_offset = project_defaults.get(tenant_id, {}) .get('end', default_end_time_offset)
                        retention_policy = project_defaults.get(tenant_id, {}) .get('rp', {})
                        self._migrate(measurement, tenant_id,
                                     start_time_offset=start_time_offset,
                                     end_time_offset=end_time_offset,
                                     retention_policy=retention_policy, **kwargs)
                    if success_file:
                        with open(success_file, 'a+') as fd:
                            fd.write('{}\n'.format(measurement))
                except Exception as e:
                    print(e, measurement)
                    if failure_file:
                        with open(failure_file, 'a+') as fe:
                            fe.write('{}\n'.format(measurement))

