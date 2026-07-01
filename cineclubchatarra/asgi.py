# ASGI para Render (compatible con WSGI)
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cineclubchatarra.settings')
application = get_asgi_application()
