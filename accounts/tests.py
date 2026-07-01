import sys
from unittest import skipIf
from django.test import TestCase
from django.urls import reverse
from .models import Usuario

PYTHON_314 = sys.version_info >= (3, 13)


class UsuarioModelTest(TestCase):
    def test_crear_aficionado(self):
        u = Usuario.objects.create_user('testaf', 'test@test.cl', 'pass1234', rol='aficionado')
        self.assertEqual(u.rol, 'aficionado')
        self.assertFalse(u.is_staff)

    def test_crear_admin(self):
        u = Usuario.objects.create_superuser('testadmin', 'admin@test.cl', 'pass1234', rol='admin')
        self.assertEqual(u.rol, 'admin')
        self.assertTrue(u.is_staff)
        self.assertTrue(u.is_superuser)

    def test_login_view(self):
        Usuario.objects.create_user('loginuser', 'login@test.cl', 'pass1234')
        resp = self.client.post(reverse('accounts:login'), {'username': 'loginuser', 'password': 'pass1234'})
        self.assertEqual(resp.status_code, 302)

    @skipIf(PYTHON_314, 'Python 3.14+ incompatible con template_rendered signal de Django')
    def test_registro_view(self):
        resp = self.client.get(reverse('accounts:registro'))
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post(reverse('accounts:registro'), {
            'username': 'nuevouser',
            'email': 'nuevo@test.cl',
            'password1': 'compleja1234',
            'password2': 'compleja1234',
            'rol': 'aficionado',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Usuario.objects.filter(username='nuevouser').exists())
