#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade build tools first
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt

# Create static directory if it doesn't exist
# mkdir -p static

# Collect static files
python manage.py collectstatic --no-input
