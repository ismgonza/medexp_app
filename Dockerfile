FROM python:3.11-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create directory for static files
RUN mkdir -p /app/staticfiles

# Create a startup script
RUN echo '#!/bin/sh' > /app/start.sh && \
    echo 'echo "DJANGO_SECRET_KEY: $DJANGO_SECRET_KEY"' >> /app/start.sh && \
    echo 'echo "All environment variables:"' >> /app/start.sh && \
    echo 'env' >> /app/start.sh && \
    echo 'python manage.py collectstatic --noinput' >> /app/start.sh && \
    echo 'gunicorn config.wsgi:application --bind 0.0.0.0:8888' >> /app/start.sh && \
    chmod +x /app/start.sh

CMD ["/app/start.sh"]