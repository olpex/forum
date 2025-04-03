#!/bin/bash

# Build script for Vercel deployment

# Make script executable
chmod +x build_files.sh

# Print Python version
python3 --version

# Install dependencies
python3 -m pip install -r requirements.txt

# Collect static files
python3 manage.py collectstatic --noinput

# Apply migrations
python3 manage.py migrate
