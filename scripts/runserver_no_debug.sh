#!/bin/bash
cd ../myvote
export DEBUG= False
export DB_NAME='myvote'
export DB_HOST='localhost'
export DB_PORT='5432'
python manage.py runserver --insecure
