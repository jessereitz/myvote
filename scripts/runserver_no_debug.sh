#!/bin/bash
cd ../myvote
export DEBUG=False
export DB_NAME='myvote'
export DB_HOST='localhost'
export DB_PORT='5432'
echo '\n\n'
echo 'WARNING: runserver_no_debug is NOT a "production mode." It still uses the django dev server. Do not use in production.'
echo '\n\n'
python manage.py runserver --insecure
