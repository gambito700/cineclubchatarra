# Rutas (URLs) de la app core
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Feed principal
    path('', views.feed, name='feed'),
    # Detalle de ciclo por slug
    path('ciclo/<slug:slug>/', views.detalle_ciclo, name='detalle_ciclo'),
    # Detalle de función por ID
    path('funcion/<int:pk>/', views.detalle_funcion, name='detalle_funcion'),
    # Línea de tiempo cronológica
    path('linea-tiempo/', views.linea_tiempo, name='linea_tiempo'),
    # Acerca de
    path('acerca-de/', views.acerca_de, name='acerca_de'),
    # Avisos
    path('avisos/', views.avisos_lista, name='avisos'),
    # Suscripción a avisos
    path('suscriptores/suscribir/', views.suscribir, name='suscribir'),
    path('suscriptores/baja/<str:token>/', views.baja_suscripcion, name='baja_suscripcion'),
    # Encuestas
    path('encuestas/', views.encuestas_lista, name='encuestas'),
    path('encuesta/<int:pk>/', views.encuesta_detalle, name='encuesta_detalle'),
    # Patrocinadores
    path('patrocinadores/', views.patrocinadores_lista, name='patrocinadores'),
    path('sala-patrocinadores/', views.sala_patrocinadores, name='sala_patrocinadores'),
    # Check-in
    path('funcion/<int:funcion_pk>/checkin/', views.checkin, name='checkin'),
    # Perfil
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/<str:username>/', views.perfil, name='perfil_usuario'),
]
