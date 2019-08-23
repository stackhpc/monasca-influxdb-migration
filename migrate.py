#! /usr/bin/env python
from helper import MigrationHelper

unit = 'd'
mult = dict(w=1, d=7)
rp_2w = dict(end=mult[unit]*2,
             rp=dict(name='2w', duration='2w', replication='1', default=True))

if __name__ == "__main__":
    default_end_time_offset = mult[unit]*52*5 # 5 years
    default_end_time_offset = mult[unit]*2 # override to 2 weeks
    tenant_defaults={
        "03cc1b94463c44e791222cb82008b8b1": rp_2w, # alaska-prod
        "703c23c3219748d484f5d863e7896317": rp_2w, # alaska-alt-1
    }

    helper = MigrationHelper(config_file='persister.conf', verbosity=0)
    helper.migrate(target_db='monasca', db_per_tenant=True,
                   skip_functions=[lambda x: x.startswith('log.')],
                   time_unit=unit,
                   tenant_defaults=tenant_defaults,
                   default_end_time_offset=default_end_time_offset,
                   default_start_time_offset=0,
                   measurements_file='migrate-measurements.log',
                   success_file='migrate-success.log',
                   failure_file='migrate-failure.log')
