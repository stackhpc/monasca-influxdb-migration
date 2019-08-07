# Getting started:

Install python requirements:

	pip install -r requirements.txt

Next, edit `influxdb_{migrate, restore}.py` as appropriate and execute:

- `influxdb_migrate.py` to migrate data from a monolithic database to a database
  per tenancy model.
- `influxdb_restore.py` to sideload data to a monolithic database from a backed
  up database.
