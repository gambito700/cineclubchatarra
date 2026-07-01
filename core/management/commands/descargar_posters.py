# Comando para obtener posters desde TMDB
# Ejecutar: python manage.py descargar_posters
# Requiere: TMDB_API_KEY o TMDB_BEARER_TOKEN en variables de entorno
import time
from pathlib import Path

import requests
from decouple import config
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from core.models import Funcion


TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p/w500'


def safe(text):
    """Reemplaza caracteres Unicode problematicos en Windows para console output."""
    if not text:
        return ''
    result = []
    for ch in text:
        if ord(ch) < 32 and ch not in ('\n', '\r', '\t'):
            continue
        if ord(ch) > 127 and ord(ch) < 160:
            # caracteres de control extendidos
            result.append('?')
        elif ch in ('\u2018', '\u2019', '\u201a', '\u201b'):
            result.append("'")
        elif ch in ('\u201c', '\u201d', '\u201e', '\u201f'):
            result.append('"')
        elif ch in ('\u2013', '\u2014'):
            result.append('-')
        elif ch in ('\u2026',):
            result.append('...')
        elif ch in ('\u00e1',):  # a con acento
            result.append('a')
        elif ch in ('\u00e9',):  # e con acento
            result.append('e')
        elif ch in ('\u00ed',):  # i con acento
            result.append('i')
        elif ch in ('\u00f3',):  # o con acento
            result.append('o')
        elif ch in ('\u00fa', '\u00fc'):  # u con acento/dieresis
            result.append('u')
        elif ch in ('\u00f1',):  # n con tilde
            result.append('n')
        elif ch in ('\u00bf', '\u00a1'):  # signos de apertura
            result.append(' ')
        elif ord(ch) > 127:
            result.append('?')
        else:
            result.append(ch)
    return ''.join(result)


class Command(BaseCommand):
    help = 'Busca posters en TMDB para funciones sin poster y los descarga localmente'

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true',
                            help='Actualizar todas las funciones (no solo las que no tienen poster)')

    def handle(self, *args, **options):
        # --- Obtener credenciales TMDB ---
        bearer_token = config('TMDB_BEARER_TOKEN', default='')
        api_key = config('TMDB_API_KEY', default='')

        if not bearer_token and not api_key:
            raise CommandError(
                'Ni TMDB_BEARER_TOKEN ni TMDB_API_KEY estan configuradas. '
                'Agregalas a .env'
            )

        # --- Preparar headers ---
        headers = {'Accept': 'application/json'}
        if bearer_token:
            headers['Authorization'] = f'Bearer {bearer_token}'
            self.stdout.write(self.style.NOTICE(safe(
                'Usando autenticacion Bearer token (TMDB API v3)'
            )))
        else:
            self.stdout.write(self.style.NOTICE(safe(
                'Usando API key como query param (legacy)'
            )))

        # --- Query: funciones sin poster (NULL o string vacio) ---
        if options['all']:
            queryset = Funcion.objects.all()
        else:
            queryset = Funcion.objects.filter(
                poster_path__isnull=True
            ) | Funcion.objects.filter(poster_path='')
            queryset = queryset.distinct()

        total = queryset.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS(safe(
                'Todas las funciones ya tienen poster.'
            )))
            return

        self.stdout.write(safe(f'Buscando posters para {total} funciones...'))

        # --- Directorio destino ---
        dest_dir = Path(__file__).resolve().parent.parent.parent.parent / 'core' / 'static' / 'core' / 'posters'
        dest_dir.mkdir(parents=True, exist_ok=True)

        encontrados = 0
        descargados = 0
        fallback_url = 0
        no_encontrados = 0

        for funcion in queryset:
            titulo_clean = funcion.titulo_pelicula.replace('(', '').replace(')', '').strip()
            # El campo en models.py se llama 'año' — accedemos via getattr seguramente
            anyo_raw = getattr(funcion, 'a\xf1o') or ''
            anyo = anyo_raw[:4] if anyo_raw else ''

            try:
                # --- Buscar en TMDB ---
                url = 'https://api.themoviedb.org/3/search/movie'
                params = {'query': titulo_clean, 'language': 'es-CL'}
                if anyo:
                    params['year'] = anyo

                if not bearer_token:
                    params['api_key'] = api_key

                resp = requests.get(url, params=params, headers=headers, timeout=10)
                if resp.status_code != 200:
                    self.stdout.write(self.style.WARNING(safe(
                        f'  Error TMDB ({resp.status_code}): {funcion.titulo_pelicula}'
                    )))
                    no_encontrados += 1
                    continue

                data = resp.json()
                results = data.get('results', [])
                if not results:
                    self.stdout.write(safe(
                        f'  - {funcion.titulo_pelicula} (no encontrada en TMDB)'
                    ))
                    no_encontrados += 1
                    continue

                poster_path_tmdb = results[0].get('poster_path')
                if not poster_path_tmdb:
                    self.stdout.write(safe(
                        f'  - {funcion.titulo_pelicula} (sin poster en TMDB)'
                    ))
                    no_encontrados += 1
                    continue

                encontrados += 1

                # --- Descargar imagen localmente ---
                slug = slugify(funcion.titulo_pelicula)[:50]
                dest_filename = f'{slug}.jpg'
                dest_path = dest_dir / dest_filename
                remote_url = f'{TMDB_IMAGE_BASE}{poster_path_tmdb}'

                try:
                    img_resp = requests.get(remote_url, timeout=15)
                    if img_resp.status_code == 200:
                        # Guardar localmente
                        with open(dest_path, 'wb') as f:
                            f.write(img_resp.content)
                        funcion.poster_path = f'/static/core/posters/{dest_filename}'
                        funcion.save()
                        descargados += 1
                        self.stdout.write(self.style.SUCCESS(safe(
                            f'  V {funcion.titulo_pelicula} -> poster descargado'
                        )))
                    else:
                        raise requests.RequestException(
                            f'HTTP {img_resp.status_code} al descargar imagen'
                        )
                except requests.RequestException as e:
                    # Fallback: guardar URL remota
                    funcion.poster_path = remote_url
                    funcion.save()
                    fallback_url += 1
                    self.stdout.write(self.style.WARNING(safe(
                        f'  ! {funcion.titulo_pelicula} -> fallback URL remota'
                    )))

            except requests.RequestException as e:
                self.stdout.write(self.style.WARNING(safe(
                    f'  Error de conexion: {e}'
                )))
                no_encontrados += 1

            time.sleep(0.25)

        # --- Resumen ---
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(safe(
            f'Posters encontrados en TMDB: {encontrados}/{total}'
        )))
        self.stdout.write(self.style.SUCCESS(safe(
            f'  - Descargados localmente: {descargados}'
        )))
        if fallback_url:
            self.stdout.write(self.style.WARNING(safe(
                f'  - URL remota como fallback: {fallback_url}'
            )))
        self.stdout.write(safe(
            f'  - No encontrados en TMDB: {no_encontrados}'
        ))

        # --- Verificar que no queden NULLs ---
        remaining = Funcion.objects.filter(poster_path__isnull=True).count()
        if remaining:
            self.stdout.write(self.style.WARNING(safe(
                f'Quedan {remaining} funciones con poster_path=NULL'
            )))
        else:
            self.stdout.write(self.style.SUCCESS(safe(
                'No quedan funciones con poster_path=NULL'
            )))
