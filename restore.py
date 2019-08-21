#! /usr/bin/env python
from helper import MigrationHelper

if __name__ == "__main__":
    helper = MigrationHelper(source_db='monasca_missing', host='192.168.7.1')
    helper.migrate(target_db='monasca', db_per_tenant=False,
                   project_defaults={
                    "03cc1b94463c44e791222cb82008b8b1": dict(end=2, rp=two_weeks), # alaska-prod
                    "703c23c3219748d484f5d863e7896317": dict(end=2, rp=two_weeks), # alaska-alt-1
                   },
                   measurements_file='restore-measurements.log',
                   success_file='restore-success.log',
                   failure_file='restore-failure.log')
