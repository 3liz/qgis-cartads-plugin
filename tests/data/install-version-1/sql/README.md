## Automatic generation of structure SQL files

### Schema cartads

Generation of the `cartads` schema SQL files is made via

```bash
cd cartads/install/sql
# 1st argument is the name of the PG Service
# 2nd argument is the name fo the PG schema
./export_database_structure_to_SQL.sh pg_cartads_service cartads
cd ../../..
make reformat_sql
```

This script will remove and regenerate the SQL files based on the `pg_dump` tool, by connecting to the database referenced by the PostgreSQL service `pg_cartads_service`.

It splits the content of the SQL dump into one file per database object type:

* functions
* tables (and comments, sequences, default values)
* views
* indexes
* triggers
* constraints (pk, unique, fk, etc.)

Files are stored in a folder which name is the schema name.
