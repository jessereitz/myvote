#!/bin/bash
cd ../myvote

export DEBUG='True'
export DB_NAME='myvote'
export DB_HOST='localhost'
export DB_PORT='5432'

if [ $1 ]
then
  python manage.py test $1
else
  python manage.py test
fi
