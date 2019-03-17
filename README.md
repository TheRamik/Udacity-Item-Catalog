# Item Catalog Web Application

A web application that provides a list of items within a variety of categories as well as providing a user registration and authentication system. Users who have registered will have the ability to post, edit, and delete their own items. Users who do not sign-in will only have access in reading the items.

## Install

Install a version of Python 2.7, Python 3.5 or both.

The next step is to install Flask as the project uses Flask as the web framework.
`$ pip install Flask`

Next, install sqlalchemy in order to connect to a sqlite3 DB.
`$ pip install sqlalchemy`

To make sure code style stays consistent, install the `pycodestyle` tool.

`$ pip install pycodestyle`

To ensure that the code stype will meet the `pycodestyle` tool's requirements, also install autopep8.

`$ pip install autopep8`


## How To Run

### Starting the Server

`$ python application.py`

Once the server is started, the web application is now accessable.

### Resetting the database

If there is ever a situation where the database needs to be reset, run the following commands:

`$ rm categorycatalogwithusers.db`
`$ python database_setup.py`
`$ python populateCategory.py`

### Accessing the Web Application

To access the web application, simply navigate to a browser and go to the link below.
`http://localhost:8000`

## Contribution Guidelines

### Making Changes to application.py

Try to keep the formatting to be as correct as possible.
Run the `pycodestyle` command to check

`$ pycodestyle application.py`

Run the `autopep8` command to automattically modify logAnalyzer.py to meet `pycodestyle` tool's requirements.

`$ autopep8 --in-place --aggressive --aggressive application.py`

### Line Length

Please keep all lines to 97 or fewer. Otherwise, the code will not pass the check with `pycodestyle`.

### JSON API

JSON enpoints are made to provide the same information as the displayed HTML endpoints. In /catalog.json, the JSON endpoint contains data from the entire database. It will display the list of categories and the items in each category. Other JSON endpoints will display the specifics of each HTML endpoint. 

### Blank Lines Between Functions

Insert two blank lines between each function.
