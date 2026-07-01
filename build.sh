#!/usr/bin/env bash
# Script de construcción para Render (sin backups — Supabase es persistente)
set -e  # Cancelar si algo falla
pip install -r requirements.txt
python manage.py migrate
python manage.py poblar_datos --if-empty
# Descargar posters desde TMDB para funciones sin poster
python manage.py descargar_posters
python manage.py collectstatic --noinput
