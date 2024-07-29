#!/bin/sh

# # Debug: Print current directory and its contents
# echo "Current directory:"
# pwd
# echo "Directory contents:"
# ls -la

# # Debug: Check if config module exists
# if [ -d "/app/config" ]; then
#     echo "config directory found"
# else
#     echo "config directory not found"
# fi

# # Run migrations
# python manage.py makemigrations
# python manage.py migrate

# # Run collectstatic
# python manage.py collectstatic --noinput

# # Start Gunicorn
# exec gunicorn config.wsgi:application --bind 0.0.0.0:8888

echo "Current directory:"
pwd
echo "Directory contents:"
ls -la

echo "Python version:"
python --version

echo "PYTHONPATH:"
echo $PYTHONPATH

echo "DJANGO_SETTINGS_MODULE:"
echo $DJANGO_SETTINGS_MODULE

echo "Content of /app directory:"
ls -R /app

echo "Attempting to import Django and config:"
python << END
import sys
print(sys.path)
try:
    import django
    print("Django imported successfully")
    import config
    print("Config imported successfully")
    print(config.__file__)
except ImportError as e:
    print(f"Import error: {e}")
END

echo "Running collectstatic:"
python manage.py collectstatic --noinput -v 3

echo "Starting Gunicorn"
exec gunicorn config.wsgi:application --bind 0.0.0.0:8888