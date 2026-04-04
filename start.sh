#!/bin/bash

# Exit on error
set -e

echo "Running Migrations..."
python manage.py migrate --noinput

echo "Collecting Static Files..."
# Already done in Dockerfile but no harm in ensuring it's fresh if needed, 
# although we prefer it in the build step to keep the image small.
# python manage.py collectstatic --noinput

echo "Creating superuser (if not exists)..."
export DJANGO_SUPERUSER_USERNAME=admin
export DJANGO_SUPERUSER_EMAIL=lcde_@hotmail.com
export DJANGO_SUPERUSER_PASSWORD=Finance@2026

python manage.py createsuperuser --noinput || echo "Superuser already exists or creation failed."

echo "Starting Gunicorn on port $PORT..."
exec gunicorn --bind 0.0.0.0:$PORT finance_system.wsgi:application
