#!/bin/sh
set -e

echo "Running database migrations..."
flask db upgrade

echo "Seeding admin and products..."
python seed_admin.py admin@bakery.com admin admin123
python seed_products.py

echo "Starting Gunicorn..."
exec gunicorn run:app --bind 0.0.0.0:$PORT