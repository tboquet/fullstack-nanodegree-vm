Tournament project
------------------

This project build an sql database and implements a basic python module to store, rank and pair the players up in matches in a tournament.

Three files are in the folder :

- `tournament.sql` is a script to create the tables in the tournament db.
- `tournament.py` is the module to insert and count data in the db.
- `tournament_test.py` is the a unit test file to verify that the module and the script actually works.

How to?
*******

1. navigate to the directory where you downloaded the files in a command prompt
2. log in the tournament db in postgreql using `psql tournament`[^1]
3. run `\i tournament.sql` in postgresql
4. quit postgersql using `\q`
5. run the `tournament_test.py` using the command `python tournament_test.py`

[^1]:
if the database is not created log in postgresql using `psql` and type `create database tournament;`.
