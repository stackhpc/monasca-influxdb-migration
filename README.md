# Getting started:

Install python requirements:

	pip install -r requirements.txt

Run `link-persister-conf.sh` to hard link to `persister.conf` in your
kolla-ansible deployed control plane.

Next, edit `{migrate, restore}.py` as appropriate and execute:

- `migrate.py` to migrate data from a monolithic database to a database
  per tenancy model.
- `restore.py` to sideload data to a monolithic database from a backed
  up database.
