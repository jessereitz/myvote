#!/bin/bash
cd ../myvote
if [ $1 ]
then
  python manage.py test $1
else
  python manage.py test
fi
