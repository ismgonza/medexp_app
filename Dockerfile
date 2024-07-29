FROM python:3.11-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings

# Install PostgreSQL client
RUN apt-get update && apt-get install -y postgresql-client

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create directory for static files
RUN mkdir -p /app/staticfiles

# Create a startup script
RUN echo '#!/bin/sh' > /app/start.sh && \
    echo 'echo "Testing database connection..."' >> /app/start.sh && \
    echo 'PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT 1;"' >> /app/start.sh && \
    echo 'python manage.py collectstatic --noinput' >> /app/start.sh && \
    echo 'gunicorn config.wsgi:application --bind 0.0.0.0:8888 --workers 4 --threads 2 --timeout 60' >> /app/start.sh && \
    chmod +x /app/start.sh

CMD ["/app/start.sh"]