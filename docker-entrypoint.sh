#!/bin/sh

# Wait for the database to be ready
until nc -z $DB_HOST $DB_PORT; do
  echo "Waiting for database to be ready..."
  sleep 2
done

# Run migrations
python manage.py migrate

# Start Gunicorn
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000