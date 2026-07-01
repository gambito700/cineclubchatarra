from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    ROLES = [
        ('admin', 'Admin'),
        ('patrocinador', 'Patrocinador'),
        ('aficionado', 'Aficionade'),
    ]
    rol = models.CharField(max_length=20, choices=ROLES, default='aficionado', verbose_name='Rol')

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def save(self, *args, **kwargs):
        if self.rol == 'admin':
            self.is_staff = True
            self.is_superuser = True
        else:
            self.is_staff = False
            self.is_superuser = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"
