#!/bin/bash
set -e
pip install --no-cache-dir -r requirements.txt
exec gunicorn wsgi:app --bind "0.0.0.0:${PORT:-8080}" --workers 2
