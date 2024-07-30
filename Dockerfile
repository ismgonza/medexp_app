# Use an official Python runtime as a parent image
FROM python:3.12-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install core dependencies.
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# # Set the entrypoint
# ENTRYPOINT ["/app/docker-entrypoint.sh"]

COPY nginx.conf /etc/nginx/nginx.conf


# Make sure gunicorn is installed
RUN pip install gunicorn

# Create a startup script in a location that won't be overwritten
RUN echo '#!/bin/sh' > /start.sh && \
    echo 'set -e' >> /start.sh && \
    echo 'cd /app' >> /start.sh && \
    echo 'until nc -z $DB_HOST $DB_PORT; do' >> /start.sh && \
    echo '  echo "Waiting for database to be ready..."' >> /start.sh && \
    echo '  sleep 2' >> /start.sh && \
    echo 'done' >> /start.sh && \
    echo 'python manage.py migrate' >> /start.sh && \
    echo 'exec gunicorn config.wsgi:application --bind 0.0.0.0:8000' >> /start.sh && \
    chmod +x /start.sh

# Set the command to run the startup script
CMD ["/start.sh"]