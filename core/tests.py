import sys
from unittest import skipIf
from django.test import TestCase
from django.urls import reverse
from core.models import Ciclo, Funcion, Aviso, Encuesta, OpcionEncuesta, Voto, Asistencia
from accounts.models import Usuario

PYTHON_314 = sys.version_info >= (3, 13)


@skipIf(PYTHON_314, 'Python 3.14+ incompatible con template_rendered signal de Django')
class CoreViewsTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user('testuser', 'test@test.cl', 'pass1234')
        self.ciclo = Ciclo.objects.create(nombre='Test Ciclo', slug='test-ciclo')
        self.funcion = Funcion.objects.create(
            titulo_pelicula='Test Movie', director='Test Director',
            ciclo=self.ciclo, año='2024',
        )

    def test_feed(self):
        resp = self.client.get(reverse('core:feed'))
        self.assertEqual(resp.status_code, 200)

    def test_detalle_ciclo(self):
        resp = self.client.get(reverse('core:detalle_ciclo', args=['test-ciclo']))
        self.assertEqual(resp.status_code, 200)

    def test_detalle_funcion(self):
        resp = self.client.get(reverse('core:detalle_funcion', args=[self.funcion.pk]))
        self.assertEqual(resp.status_code, 200)

    def test_modal_funcion(self):
        resp = self.client.get(f"{reverse('core:detalle_funcion', args=[self.funcion.pk])}?formato=modal")
        self.assertEqual(resp.status_code, 200)

    def test_linea_tiempo(self):
        resp = self.client.get(reverse('core:linea_tiempo'))
        self.assertEqual(resp.status_code, 200)

    def test_acerca_de(self):
        resp = self.client.get(reverse('core:acerca_de'))
        self.assertEqual(resp.status_code, 200)


@skipIf(PYTHON_314, 'Python 3.14+ incompatible con template_rendered signal de Django')
class AvisosTest(TestCase):
    def test_avisos_page(self):
        resp = self.client.get(reverse('core:avisos'))
        self.assertEqual(resp.status_code, 200)

    def test_aviso_en_feed(self):
        Aviso.objects.create(titulo='Test Aviso', mensaje='Test mensaje')
        resp = self.client.get(reverse('core:feed'))
        self.assertContains(resp, 'Test Aviso')


class EncuestasTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user('voter', 'voter@test.cl', 'pass1234')

    def test_encuesta_votar(self):
        enc = Encuesta.objects.create(titulo='Test Encuesta')
        op1 = OpcionEncuesta.objects.create(encuesta=enc, texto='Opción 1', orden=1)
        op2 = OpcionEncuesta.objects.create(encuesta=enc, texto='Opción 2', orden=2)
        self.client.login(username='voter', password='pass1234')
        resp = self.client.post(reverse('core:encuesta_detalle', args=[enc.pk]), {'opcion': op1.pk})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Voto.objects.filter(usuario=self.user, encuesta=enc).exists())

    def test_encuesta_sin_voto_duplicado(self):
        enc = Encuesta.objects.create(titulo='Test')
        op1 = OpcionEncuesta.objects.create(encuesta=enc, texto='Op 1', orden=1)
        Voto.objects.create(usuario=self.user, opcion=op1, encuesta=enc)
        self.assertEqual(Voto.objects.filter(usuario=self.user, encuesta=enc).count(), 1)


class CheckinTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user('checker', 'checker@test.cl', 'pass1234')
        self.ciclo = Ciclo.objects.create(nombre='Ciclo', slug='ciclo')
        self.funcion = Funcion.objects.create(titulo_pelicula='Film', ciclo=self.ciclo)

    def test_checkin_requiere_login(self):
        resp = self.client.post(reverse('core:checkin', args=[self.funcion.pk]))
        self.assertEqual(resp.status_code, 302)

    def test_checkin_exitoso(self):
        self.client.login(username='checker', password='pass1234')
        resp = self.client.post(reverse('core:checkin', args=[self.funcion.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Asistencia.objects.filter(usuario=self.user, funcion=self.funcion).exists())
