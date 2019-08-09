from __future__ import print_function
import influxdb

migrate_query_template = 'SELECT * INTO "{target_db}"..:MEASUREMENT FROM "{measurement}" WHERE _tenant_id=\'{tenant_id}\' AND time >= {time_offset} LIMIT {limit}'
select_query_template = 'SELECT * FROM "{measurement}" WHERE _tenant_id=\'{tenant_id}\' AND time >= {time_offset} LIMIT {limit} OFFSET {offset}'

class MigrationHelper(object):

    def __init__(self, source_db, host, verbosity=1):
        self.client = influxdb.InfluxDBClient(host=host, database=source_db)
        self.verbosity = verbosity


    def _migrate(self, measurement, tenant_id, limit, time_offset, target_db, db_per_tenant, epoch='ns'):
        total_written = 0
        if db_per_tenant:
            target_db = "{}_{}".format(target_db, tenant_id)
        self.client.create_database(target_db)
        while True:
            migrate_query = migrate_query_template.format(target_db=target_db,
                                                          measurement=measurement,
                                                          tenant_id=tenant_id,
                                                          time_offset=time_offset,
                                                          limit=limit)
            if total_written == 0 and self.verbosity > 0:
                print(migrate_query)

            written = next(self.client.query(migrate_query).get_points('result')).get('written')
            total_written += written
            if written > 0:
                select_query = select_query_template.format(measurement=measurement,
                                                            tenant_id=tenant_id,
                                                            time_offset=time_offset,
                                                            limit=1,
                                                            offset=written)
                try:
                    raw_time_offset = next(self.client.query(select_query, epoch=epoch).get_points(measurement))
                    time_offset = '{}{}'.format(raw_time_offset.get('time'), epoch)
                    if (self.verbosity > 1 or
                        (self.verbosity > 0 and
                         (total_written - written) % (limit * 10))):
                        print("{}: migrated {} entries until {} into {}".format(measurement,
                                                                                total_written,
                                                                                time_offset,
                                                                                target_db))
                    else:
                        print(".", end="")
                except StopIteration:
                    break
            else:
                break

        print("{}: migrated {} entries into {}".format(measurement,
                                                       total_written,
                                                       target_db))

    def get_measurements(self, fname):
        if fname:
            with open(fname) as fm:
                return [l.strip() for l in fm.readlines()]
        else:
            return [m.get('name') for m in self.client.query('SHOW MEASUREMENTS').get_points('measurements')]

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
                start_time_offset={},
                limit=50000,
                target_db='monasca',
                db_per_tenant=True,
                measurements_file=None,
                success_file=None,
                failure_file=None):
        measurements = self.get_measurements(measurements_file)
        tenancy = self.get_tenancy(measurements)
        done = self.get_complete(success_file)
        for measurement in measurements:
            if measurement in done or measurement.startswith('log.'):
                print('Skipping {}'.format(measurement))
            else:
                try:
                    for tenant_id in tenancy.get(measurement):
                        time_offset = start_time_offset.get(tenant_id, '0')
                        self._migrate(measurement, tenant_id,
                                     time_offset=time_offset,
                                     limit=limit,
                                     target_db=target_db,
                                     db_per_tenant=db_per_tenant)
                    if success_file:
                        with open(success_file, 'a+') as fd:
                            fd.write('{}\n'.format(measurement))
                except Exception as e:
                    print(e, measurement)
                    if failure_file:
                        with open(failure_file, 'a+') as fe:
                            fe.write('{}\n'.format(measurement))
