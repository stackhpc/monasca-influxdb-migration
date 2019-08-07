#! /usr/bin/env python
import influxdb
source_db = 'monasca_missing'
target_db = 'monasca_target'
host = '192.168.7.1'
client = influxdb.InfluxDBClient(host=host, database=source_db)
measurements = [m.get('name') for m in client.query('SHOW MEASUREMENTS').get_points('measurements')]
print(measurements)
with open('done.txt', 'a+') as fd:
    done = {l.strip() for l in fd.readlines()}
    for measurement in measurements:
        if measurement in done:
            print('Skipping {}'.format(measurement))
        else:
            query = 'SELECT * INTO {}..:MEASUREMENT FROM "{}" GROUP BY *'.format(target_db, measurement)
            print(query)
            try:
                print(client.query(query))
                fd.write('{}\n'.format(measurement))
            except Exception as e:
                print(e, measurement)
