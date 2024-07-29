#!/bin/sh

python manage.py migrate
gunicorn medexp_app.wsgi:application --bind 0.0.0.0:8888