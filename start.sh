#!/bin/sh

python manage.py migrate
python manage.py collectstatic --noinput
gunicorn medexp_app.wsgi:application --bind 0.0.0.0:8888