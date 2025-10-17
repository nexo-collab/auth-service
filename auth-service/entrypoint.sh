#!/bin/sh

set -e

echo "⏳ Waiting for Postgres with pg_isready ($POSTGRES_HOST:$POSTGRES_PORT) ..."
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" >/dev/null 2>&1; do
  echo "🟡 Waiting for Postgres Database Startup ($POSTGRES_HOST:$POSTGRES_PORT) ..."
  sleep 2
done

echo "✅ Postgres Database Started Successfully ($POSTGRES_HOST:$POSTGRES_PORT)"

python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:8000