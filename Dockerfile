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
RUN python -c "import sys; print(sys.executable)"
RUN python -c "import django; print(django.__file__)"
RUN python -c "from django.conf import settings; print(settings.BASE_DIR)"
RUN python -c "from django.conf import settings; print(settings.STATIC_ROOT)"
RUN python -c "from django.conf import settings; print(settings.STATIC_URL)"
RUN python -c "from django.conf import settings; print(settings.STATICFILES_DIRS)"
RUN python -c "import os; print(os.listdir(settings.BASE_DIR))"
RUN echo $DJANGO_SETTINGS_MODULE

# Collect static files
RUN python manage.py collectstatic --noinput -v 3

CMD ["gunicorn", "--config", "gunicorn.conf.py", "config.wsgi:application"]