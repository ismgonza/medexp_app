# Use an official Python runtime as a parent image
FROM python:3.12.2-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
# RUN apt-get update && apt-get install -y netcat

# Install Python dependencies
COPY requirements.txt /app/
# RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]

RUN chmod +x /app/docker-entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]