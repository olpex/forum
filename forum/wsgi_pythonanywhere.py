"""
WSGI config for forum project on PythonAnywhere.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
import sys

# Add your project directory to the sys.path
path = '/home/yourusername/forum'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'forum.settings'
os.environ['DJANGO_SECRET_KEY'] = 'your-secret-key-here'  # Replace with your actual secret key
os.environ['DJANGO_DEBUG'] = 'False'

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
