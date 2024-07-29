FROM python:3.11-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=config.settings

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

# Diagnostic commands
RUN python --version
RUN pip list
RUN echo $DJANGO_SETTINGS_MODULE
RUN ls -R /app

# Collect static files
RUN python manage.py collectstatic --noinput -v 3

CMD ["gunicorn", "--config", "gunicorn.conf.py", "config.wsgi:application"]