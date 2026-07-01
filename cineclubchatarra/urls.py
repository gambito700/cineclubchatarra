# Urls principales del proyecto Cine Chatarra
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # Autenticación
    path('', include('core.urls')),  # Todas las rutas de la app core
]
