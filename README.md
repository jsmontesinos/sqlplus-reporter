# sqlplus-reporter

Sqlplus Reporter is a report generator for SQL plus from Oracle Databases.

The only thing you have to do is give a sql file with the query (-i) and a connection string (-c) configured in *tnsnames.ora* or in *host:port/service* format if you are using SQL plus version 11 or newer.

You can find other script options in the script help.

## Example

To launch the script:

    python makereport.py -i query.sql -c "user/pass@local_SID"
