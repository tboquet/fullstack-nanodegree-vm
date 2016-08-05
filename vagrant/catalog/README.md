Item catalog
-------------

This project is an item catalog application.

five files are in the folder:

- `database_setup.py` is a script to create the tables in the db and a module that define the structure of the tables.
- `lotsofitems.py` is a script to insert data in the db.
- `client_secrets.json` is a file containing the information about google login.
- `fb_client_secrets.json` is a file containing the information about facebook login.
- `catalogitem.py` is a script that implements the application.

 To run it:
===========

1. Navigate to the directory where you downloaded the files
2. run the `database_setup.py` script to create the tables in the db
3. run the `lotsofitems.py` script to populate the database
4. run the `catalogitem.py` script to launch the application

Go to `localhost:5000` in a web browser.

You can access several json endpoints:

- all the items in one category: `/category/<category_name>/JSON`
- all the items in the database: `/category/all/JSON`
- one specific item in the database: `/category/<category_name>/<item_name>/JSON`
- all the categories in the database: `/category/JSON`
