#! /usr/bin/env python
from helper import MigrationHelper, two_weeks

if __name__ == "__main__":
    helper = MigrationHelper(source_db='monasca', host='10.114.125.10', verbosity=0)
    helper.migrate(target_db='monasca', db_per_tenant=True,
                   project_defaults={
                    "a7c73dd77aac4152b41a7a8fc15c82aa": dict(end=2, rp=two_weeks), # verne-candidate
                   },
                   measurements_file='migrate-measurements.log',
                   success_file='migrate-success.log',
                   failure_file='migrate-failure.log')
