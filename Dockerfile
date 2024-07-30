# Use an official Python runtime as a parent image
FROM python:3.12-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install core dependencies.
RUN apt-get update && apt-get install -y libpq-dev build-essential && apt-get install -y netcat

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]

RUN chmod +x /app/docker-entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]