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

# # Copy entrypoint script
# COPY docker-entrypoint.sh /app/docker-entrypoint.sh

# # Set correct permissions for entrypoint script
# RUN chmod +x /app/docker-entrypoint.sh

# Copy project
COPY . /app/

# # Set the entrypoint
# ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Make sure gunicorn is installed
RUN pip install gunicorn

# Create a startup script
RUN echo '#!/bin/sh' > /app/start.sh && \
    echo 'set -e' >> /app/start.sh && \
    echo 'until nc -z $DB_HOST $DB_PORT; do' >> /app/start.sh && \
    echo '  echo "Waiting for database to be ready..."' >> /app/start.sh && \
    echo '  sleep 2' >> /app/start.sh && \
    echo 'done' >> /app/start.sh && \
    echo 'python manage.py migrate' >> /app/start.sh && \
    echo 'exec gunicorn config.wsgi:application --bind 0.0.0.0:8000' >> /app/start.sh && \
    chmod +x /app/start.sh

# Set the command to run the startup script
CMD ["/app/start.sh"]