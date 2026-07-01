# Entry point WSGI para Gunicorn / Render
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cineclubchatarra.settings')
application = get_wsgi_application()
