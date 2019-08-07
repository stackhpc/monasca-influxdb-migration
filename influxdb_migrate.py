#! /usr/bin/env python
from influxdb_helper import MigrationHelper

if __name__ == "__main__":
    helper = MigrationHelper(source_db='monasca', host='192.168.7.1')
    helper.migrate(target_db='monasca', db_per_tenant=True,
                   start_time_offset=1565192859703000000,
                   measurements_file='migrate-test.txt',
                   success_file='migrate-success.txt',
                   failure_file='migrate-failure.txt')
