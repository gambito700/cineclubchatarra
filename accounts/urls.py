from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginPersonalizado.as_view(), name='login'),
    path('registro/', views.registro, name='registro'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
