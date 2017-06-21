# OpenODS Import Tool

This is an import tool for creating the SQL database for OpenODS.

This repository uses Git Flow workflow:

- master - for periodic stable releases
- develop - for ongoing development work
- feature/??? - for branched feature development

If you are looking for the latest version of the code,
check develop branch first.

## Importing the ODS XML data into an OpenODS database
### Pre-requisites
* SQLite or PostgreSQL (the API service requires PostgreSQL so SQLite just for database testing)
* A way of running SQL queries against PostgreSQL (I use psql or [pgAdmin](http://www.pgadmin.org/download/macosx.php))
* All setup steps in the main README should be completed

### Steps

1. Activate your Python 3 virtualenv (if you are using one) and make sure the requirements are all installed

    ```bash
    $ pip install -r requirements.txt
    ```

2. From the root of your repo directory, run the database import script

    ```bash
    $ python import.py
    ```

For details of available arguments, run:

```bash
    $ python import.py -h
```

All of the arguments are optional, and without them the script will just use its default DBMS, file locations, and connection string.

### Examples

To import the data to a SQLLite database:

```bash
$ python import.py -d sqlite -c sqlite:///openods.db --verbose

Import Completed.
```

## More Documentation

[Importing / Exporting with PostgreSQL](docs/importing_exporting_psql.md)

[Restoring to Heroku](docs/restoring_to_heroku_pg.md)
