# MyVote
**A simple online polling platform**

## Overview
MyVote is a simple polling platform written on top of the Django framework for Python.

## Purpose
I started this project with the intent on honing my Python skills and to familiarize myself with the Django web framework.

## Skills Learned
Throughout the course of this project my skill level and comfort level with Django, and, more broadly, Python, have increased drastically. My conceptualization and understanding of data models has also improved over the evolution of this project. I feel confident these skills will be transferrable to any and all future projects, whether they be written in Django or another web framework.

## Installing
If you would like to run this application locally, simple follow these steps:

1. Clone repo locally
2. In the root of the cloned repo, create a virtual environment: `virtualenv -p python3 venv`
3. Activate virtual environment: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. CD into the scripts directory
6. Ensure the database is up to date:
```
sh makemigrations.sh
sh migrate.sh
```
7. Run the application: `sh runserver.sh`
