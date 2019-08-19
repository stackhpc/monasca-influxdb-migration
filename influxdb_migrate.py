#! /usr/bin/env python
from influxdb_helper import MigrationHelper

if __name__ == "__main__":
    helper = MigrationHelper(source_db='monasca', host='192.168.7.1')
    helper.migrate(target_db='monasca', db_per_tenant=True,
                   limit=25000,
                   default_time_offset="now()-2w",
                   start_time_offset={
                    "03cc1b94463c44e791222cb82008b8b1": "now()-2w", # alaska-prod
                    "703c23c3219748d484f5d863e7896317": "now()-2w", # alaska-alt-1
                   },
                   success_file='migrate-success.txt',
                   failure_file='migrate-failure.txt')
