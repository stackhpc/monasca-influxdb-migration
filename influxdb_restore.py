#! /usr/bin/env python
from influxdb_helper import MigrationHelper

if __name__ == "__main__":
    helper = MigrationHelper(source_db='monasca_missing', host='192.168.7.1')
    helper.migrate(target_db='monasca', db_per_tenant=True,
                   start_time_offset=1543511354640000000,
                   success_file='restore-success.txt',
                   failure_file='restore-failure.txt')
