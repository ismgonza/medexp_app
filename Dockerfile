FROM python:3.11-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings
ENV DJANGO_DEBUG=False

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

COPY . /app/

# Create staticfiles directory
RUN mkdir -p /app/staticfiles

# Diagnostic commands
RUN python --version
RUN pip list
RUN echo $DJANGO_SETTINGS_MODULE
RUN ls -R /app
RUN python -c "import django; print(django.__version__)"
RUN python manage.py check --deploy
RUN ls -R /app/static || echo "No static directory found"

# Collect static files
RUN python manage.py collectstatic --noinput -v 3 || { echo "Collectstatic failed"; python manage.py collectstatic --noinput -v 3; exit 1; }

CMD ["gunicorn", "--config", "gunicorn.conf.py", "config.wsgi:application"]