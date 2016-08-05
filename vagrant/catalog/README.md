Item catalog
-------------

This project is an item catalog application.

five files are in the folder :

- `database_setup.py` is a script to create the tables in the db and a module that define the structure of the tables.
- `lotsofitems.py` is a script to insert data in the db.
- `client_secrets.json` is a file containing the information about google login.
- `fb_client_secrets.json` is a file containing the information about facebook login.
- `catalogitem.py` is a script that implements the application.

 To run it:
 ~~~~~~~~~~

1. Navigate to the directory where you downloaded the files
2. run the `database_setup.py` script to create the tables in the db
3. run the `lotsofitems.py` script to populate the database
4. run the `catalogitem.py` script to launch the application
