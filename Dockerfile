FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y libpq-dev gcc netcat-traditional && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/
RUN python manage.py collectstatic --noinput

# Railway automatically sets the PORT environment variable
ENV PORT=8000
EXPOSE $PORT

CMD gunicorn --bind 0.0.0.0:$PORT finance_system.wsgi:application
