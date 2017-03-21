## Importing / Exporting with PostgreSQL

### Notes

* If you are deploying OpenODS on a vanilla server, you may be able to run the import routine on the server itself (note the routine is RAM heavy).

* If you are deploying somewhere where it is not an option to run the import on the server itself (e.g. Heroku or a low-powered VPS) then you will need to run the import on a local machine and then restore the database to your deployed instance.
 
**Remember to always make sure that the schema version of the database you are using matches the expected schema version of the deployed application (see config.py)**

### Importing the XML data to Postgres
You will need to ensure you have an instance of Postgres installed on the machine that you want to run the import on (Postgres.app is easy and self-contained if you are using OSX).

First create an 'openods' user on your Postgres server

```bash
$ psql -c "CREATE USER openods WITH PASSWORD 'openods';"
```

Now create an empty database (I usually call it 'openods') and set the owner to user you created in the previous step

```bash
$ psql -c "CREATE DATABASE openods OWNER openods;"
```

Run the import routine in Postgres mode ensuring the connection string matches the database and role you just created

```bash
$ python import.py -d postgres -c postgresql://openods:openods@localhost/openods --verbose

Import Completed.
```
    
*You might want to use your preferred database tool to check that the data has imported correctly.*
    
### Exporting the PostgreSQL database to a backup file

You can easily export the Postgres database so that it can be restored to other instances of Postgres.

From a terminal, run the following command to export the database to a file.

This runs an export as the Postgres master user (and so assumes that you have the permissions on the Postgres server to do this).

```bash
$ pg_dump -Fc --no-acl --no-owner -h localhost -U postgres openods > openods.dump
```

You should now have a file called openods.dump containing a compressed backup of your openods database.
You can choose a filename (and extension) that suits you.

### Importing the database backup file to a PostgreSQL instance

*Note: This assumes that you have a Postgres server setup and configured with the same role / user as used in your source database.*

1. As we exported the database using the Postgres custom compressed format, we use the pg_restore command to restore the database from the file:

```bash
$ pg_restore -d openods openods_010.dump
```

2. You could then run the following in the terminal to confirm that the correct version of the database has been restored:

```bash
$ psql -d openods -c "SELECT * from settings;"

      key       | value
----------------+-------
 schema_version | 010
(1 row)

$
```