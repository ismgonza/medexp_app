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

# Install requirements again to ensure all packages are installed
RUN pip install --no-cache-dir -r requirements.txt

RUN echo "DJANGO_SECRET_KEY: $DJANGO_SECRET_KEY"

# We'll collect static files at runtime instead of build time
CMD ["sh", "-c", "python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000"]