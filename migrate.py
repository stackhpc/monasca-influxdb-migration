#! /usr/bin/env python
from helper import MigrationHelper

multiplier = 7
two_weeks = dict(name='2w', duration='2w', replication='1', default=True)

if __name__ == "__main__":
    helper = MigrationHelper(config_file='persister.conf', verbosity=0)
    helper.migrate(target_db='monasca', db_per_tenant=True,
                   project_defaults={
                    "03cc1b94463c44e791222cb82008b8b1": dict(end=2*multiplier, rp=two_weeks), # alaska-prod
                    "703c23c3219748d484f5d863e7896317": dict(end=2*multiplier, rp=two_weeks), # alaska-alt-1
                   },
                   skip_functions=[lambda x: x.startswith('log.')],
                   time_unit='d',
                   default_end_time_offset=1*multiplier,
                   #default_end_time_offset=52*5*multiplier,
                   default_start_time_offset=0,
                   measurements_file='migrate-measurements.log',
                   success_file='migrate-success.log',
                   failure_file='migrate-failure.log')
