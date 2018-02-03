#!/bin/bash
cd ../myvote
export DEBUG='True'
export DB_NAME='myvote'
export DB_HOST='localhost'
export DB_PORT='5432'
python manage.py migrate
