# MyVote
**A simple online polling platform**

## Overview
MyVote is a simple polling platform written on top of the Django framework for Python.

## Purpose
I started this project with the intent on honing my Python skills and to familiarize myself with the Django web framework.

## Skills Learned
Throughout the course of this project my skill level and comfort level with Django, and, more broadly, Python, have increased drastically. My conceptualization and understanding of data models has also improved over the evolution of this project. I feel confident these skills will be transferrable to any and all future projects, whether they be written in Django or another web framework.

## Installing
There are ___ main parts to setting up MyVote locally.

First, ensure you have Postgres installed and running on your system. I suggest using [Postgress.app](https://postgresapp.com/) <a href="https://postgresapp.com/" target="_blank">Postgress.app</a> but any method of running Postgres should work. Once you have Postgres installed and running, you will need to create a database. Remember its name, host uri, port number, and username/password (if applicable). You will use these later.

Next, set up your local environment:
1. Clone repo locally
2. In the root of the cloned repo, create a virtual environment:
```
virtualenv -p python3 venv
```
3. Activate virtual environment:
```
source venv/bin/activate
```
4. Install dependencies:
```
pip install -r requirements.txt
```
5. Set your environment variables:
```
$ export DEBUG='True/False'
$ export DB_NAME='myvote'
$ export DB_USER='your_db_username'
$ export DB_PASSWORD='your_db_password'
$ export DB_HOST='localhost'
$ export DB_PORT='5432'
```
6. CD into the scripts directory
7. Ensure the database is up to date:
```
sh makemigrations.sh
sh migrate.sh
```

Finally, run the server using one of the following methods:
1. Debug mode:
```
sh runserver.sh
```
2. Non-debug mode (note, this is not a "production mode". This method uses the Django dev server while still allowing you to view the custom error pages):
```
sh runserver_non_debug.sh
```
3. Manually (re)-set your environment variable and run the application through the manage.py file (found in the myvote directory):
```
$ export DEBUG='True/False'
$ export DB_NAME='myvote'
$ export DB_USER='your_db_username'
$ export DB_PASSWORD='your_db_password'
$ export DB_HOST='localhost'
$ export DB_PORT='5432'
python manage.py runserver
```
