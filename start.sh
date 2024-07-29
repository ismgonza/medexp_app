#!/bin/sh

# Debug: Print current directory and its contents
echo "Current directory:"
pwd
echo "Directory contents:"
ls -la

# Debug: Check if config module exists
if [ -d "/app/config" ]; then
    echo "config directory found"
else
    echo "config directory not found"
fi

# Run migrations
python manage.py migrate

# Start Gunicorn
exec gunicorn config.wsgi:application --bind 0.0.0.0:8888