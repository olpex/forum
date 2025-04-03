"""
WSGI config for forum project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

# Add the project directory to the sys.path
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forum.settings")

# For Vercel deployment
os.environ["DJANGO_ALLOWED_HOSTS"] = ".vercel.app"
os.environ["DJANGO_DEBUG"] = "False"

application = get_wsgi_application()

# Handler for Vercel serverless function
app = application
