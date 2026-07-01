# 🎬 INSTRUCTIVO — Deploy de Cine Club Chatarra en Render

> **Proyecto**: cineclubchatarra  
> **Repo**: https://github.com/gambito700/cineclubchatarra  
> **Rama**: `main`  
> **Último commit**: `67d8976`  
> **Fecha**: 30 de junio de 2026

---

## 📋 Índice

1. [Diagnóstico de Problemas](#1-diagnóstico-de-problemas)
2. [Plan de Acción](#2-plan-de-acción-paso-a-paso)
   - [Paso 1: Limpiar requirements.txt](#paso-1-limpiar-requirementstxt)
   - [Paso 2: Commit y push a GitHub](#paso-2-commit-y-push-a-github)
   - [Paso 3: Configurar entorno en Render](#paso-3-configurar-entorno-en-render-usando-blueprint)
   - [Paso 4: Forzar Python 3.11](#paso-4-forzar-python-311)
   - [Paso 5: Configurar variables de entorno](#paso-5-configurar-variables-de-entorno)
   - [Paso 6: Generar contraseña de aplicación de Google (GMAIL_PASSWORD)](#paso-6-generar-contraseña-de-aplicación-de-google)
   - [Paso 7: Verificar start command](#paso-7-verificar-start-command)
   - [Paso 8: Hacer deploy](#paso-8-hacer-deploy)
   - [Paso 9: Post-deploy — migraciones y datos](#paso-9-post-deploy--migraciones-y-datos)
3. [Checklist de Verificación](#3-checklist-de-verificación)
4. [Referencias](#4-referencias)

---

## 1. Diagnóstico de Problemas

### Problema 1: easyocr descarga ~2GB de dependencias CUDA/torch

```
# requirements.txt (ACTUAL)
easyocr==1.7.2
```

**¿Qué ocurre?**  
`easyocr==1.7.2` declara como dependencia `torch`. Cuando pip resuelve las dependencias, descarga wheels de CUDA (`nvidia_*`, `triton`, etc.) que suman **~2 GB**. En un entorno con recursos limitados como Render (gratuito: 512 MB RAM, <1 CPU), esto:

- Agota el tiempo de build (límite ~15 min en plan gratuito)
- Llena el caché de pip con wheels CUDA innecesarios
- Causa errores de "hash mismatch" porque pip en Render puede tener `--require-hashes` activado y los wheels de torch/nvidia no coinciden

**¿Dónde se usa?**  
Únicamente en el comando de gestión `importar_posters_instagram.py`, línea 243:
```python
import easyocr
reader = easyocr.Reader(['es', 'en'], gpu=False)
```

**¿Se ejecuta en producción/build?**  
**NO**. El archivo `build.sh` NO ejecuta `importar_posters_instagram`. Los comandos en build.sh son:

1. `pip install -r requirements.txt`
2. `python manage.py migrate`
3. `python manage.py poblar_datos --if-empty`
4. `python manage.py descargar_posters`
5. `python manage.py collectstatic --noinput`

Ningún `view.py`, `admin.py` ni otro archivo usado en producción importa `easyocr`.

**Impacto**: Alto. El build falla antes de siquiera empezar por timeouts y hash mismatches.

---

### Problema 2: Pillow y unidecode innecesarios en producción

```
# requirements.txt (ACTUAL)
Pillow==11.1.0
unidecode==1.3.8
```

**Pillow**: Solo se usa en `importar_posters_instagram.py` línea 71 (`from PIL import Image`) para convertir imágenes HEIC a JPG. Ninguna vista, modelo o admin lo necesita. Django usa `URLField` para posters (no `ImageField`), así que Pillow es irrelevante para producción.

**unidecode**: **NO SE USA EN NINGÚN ARCHIVO DEL PROYECTO**. La función `normalize()` en `importar_posters_instagram.py` usa `unicodedata` (biblioteca estándar de Python), no `unidecode`. `unidecode` es una dependencia muerta.

**Impacto**: Medio-Bajo. Aunque no rompen el build, aumentan el tiempo de instalación innecesariamente.

---

### Problema 3: Render usa Python 3.14 en vez de 3.11

Aunque `runtime.txt` especifica `python-3.11.0` y `render.yaml` tiene `PYTHON_VERSION=3.11.0`, Render ignora estas configuraciones cuando se hace deploy manual desde el dashboard.

**Causa raíz**: 

- `runtime.txt` es respetado por **Heroku**, pero Render solo lo usa parcialmente (y a veces lo ignora).
- `render.yaml` con `PYTHON_VERSION` solo funciona si haces **Blueprint deploy** (conectar repo + Render usa el `render.yaml`). Si creaste el servicio manualmente desde el dashboard, `render.yaml` no se lee.
- Render detecta el lenguaje y elige la versión default de Python (hoy: 3.14).

**Impacto**: Alto. Los wheels compilados para `cp314` pueden no ser compatibles con versiones anteriores. Django 5.1.15 puede tener issues con Python 3.14.

---

### Problema 4: Start command incorrecto (usa default)

Render ejecutó `gunicorn app:app` (el default de la plataforma) en vez de:

```
gunicorn cineclubchatarra.wsgi:application --workers 2 --threads 2 --bind 0.0.0.0:$PORT
```

**Causa**: Si creaste el servicio manual desde el dashboard, Render ignora `render.yaml` y usa su configuración default. El start command default es `gunicorn app:app`, que no existe en el proyecto.

**Impacto**: Alto. El servicio nunca arranca porque no encuentra `app:app`.

---

### Problema 5: GMAIL_PASSWORD no configurada

`GMAIL_PASSWORD` aparece como `sync: false` en `render.yaml` (debe ser ingresada manualmente). Sin este valor:

- El backend de email se configura como `console.EmailBackend` (no envía correos reales)
- Los avisos por email no funcionan
- No hay error fatal — la app funciona, pero el email está caído

---

### Problema 6: Variables de entorno sin configurar

Varias variables marcadas como `sync: false` en `render.yaml` deben ser ingresadas manualmente en el dashboard de Render. Sin ellas, la app falla al arrancar o funciona parcialmente.

---

## 2. Plan de Acción (Paso a Paso)

### Paso 1: Limpiar requirements.txt

Elimina `easyocr`, `Pillow` y `unidecode` de `requirements.txt`, ya que solo se usan en el comando de importación local.

**Archivo**: `C:\Users\HP VICTUS\Downloads\instagram-cine_chatarra-2026-06-29-jk0bc0x\Nueva carpeta\cineclubchatarra\requirements.txt`

**Antes** (11 líneas):
```txt
Django==5.1.15
gunicorn==23.0.0
whitenoise==6.9.0
psycopg2-binary==2.9.10
python-decouple==3.8
dj-database-url==2.3.0
requests==2.32.3
django-ratelimit==4.1.0
easyocr==1.7.2      ← ELIMINAR
Pillow==11.1.0      ← ELIMINAR
unidecode==1.3.8    ← ELIMINAR
```

**Después** (8 líneas):
```txt
Django==5.1.15
gunicorn==23.0.0
whitenoise==6.9.0
psycopg2-binary==2.9.10
python-decouple==3.8
dj-database-url==2.3.0
requests==2.32.3
django-ratelimit==4.1.0
```

> ⚠️ **Nota**: Las dependencias eliminadas (`easyocr`, `Pillow`, `unidecode`) solo se usan localmente en `importar_posters_instagram.py`. Si en el futuro necesitas ejecutar ese comando en Render, lo harás desde tu máquina local contra la base de datos remota, o crearás un comando separado. En producción, no hay ninguna función que las requiera.

---

### Paso 2: Commit y push a GitHub

Una vez modificado `requirements.txt`:

```powershell
# Terminal (PowerShell) — desde la carpeta del proyecto:
cd C:\Users\HP VICTUS\Downloads\instagram-cine_chatarra-2026-06-29-jk0bc0x\Nueva carpeta\cineclubchatarra

git add requirements.txt
git commit -m "fix: remove heavy deps (easyocr, Pillow, unidecode) from production requirements — only needed locally for import_posters_instagram"
git push origin main
```

> El push puede pedirte credenciales de GitHub. Usa un **token personal** (no tu contraseña de GitHub):
> 1. Ve a https://github.com/settings/tokens
> 2. Genera un token con permisos `repo`
> 3. Copia el token y úsalo como contraseña cuando git lo pida

---

### Paso 3: Configurar entorno en Render usando Blueprint (IMPORTANTE)

> **⚠️ CRÍTICO**: Para que Render lea `render.yaml` y `runtime.txt`, debes hacer **Blueprint deploy**, no "New Web Service" manual.

**Opción A (RECOMENDADA) — Blueprint desde el dashboard:**

1. Ve a https://dashboard.render.com
2. Haz clic en **"New +"** → **"Blueprint"**
3. Conecta tu cuenta de GitHub si no lo has hecho
4. Selecciona el repositorio `gambito700/cineclubchatarra`
5. Render detectará automáticamente el `render.yaml`
6. Haz clic en **"Apply Blueprint"**

**Opción B — Si ya tienes un servicio web creado manualmente:**

1. Ve a https://dashboard.render.com
2. Busca tu servicio existente
3. Ve a **Settings** → haz scroll hasta abajo
4. Haz clic en **"Delete Web Service"** (confirma la eliminación)
5. Vuelve al paso **Opción A**

> La Opción B es necesaria porque un servicio creado manualmente **ignora** `render.yaml` y `runtime.txt`.

---

### Paso 4: Forzar Python 3.11

Ya tienes los archivos correctos. El Blueprint deploy leerá ambos:

**`runtime.txt`** (ya existe — verificar contenido):
```
python-3.11.0
```

**`render.yaml`** (ya existe — verificar que tenga `PYTHON_VERSION`):
```yaml
envVars:
  - key: PYTHON_VERSION
    value: 3.11.0
```

**Verificación**: Durante el build, revisa los logs de Render. Debes ver algo como:

```
==> Using Python 3.11.0
...
Collecting Django==5.1.15
  Downloading Django-5.1.15-py3-none-any.whl (8.3 MB)
```

Si ves `cp314` en los wheels, algo está mal (probablemente no usaste Blueprint deploy).

---

### Paso 5: Configurar variables de entorno

Después del Blueprint deploy, Render creará el servicio pero **algunas variables quedan pendientes** (las marcadas con `sync: false`). Debes ingresarlas manualmente.

Ve a tu servicio en Render Dashboard → **Environment** → y agrega/verifica cada una:

| Variable | Valor | ¿Sync? |
|----------|-------|--------|
| `DJANGO_SETTINGS_MODULE` | `cineclubchatarra.settings` | ✅ Auto |
| `PYTHON_VERSION` | `3.11.0` | ✅ Auto |
| `DEBUG` | `False` | ✅ Auto |
| `SECRET_KEY` | *(generado automáticamente por Render)* | ✅ Auto |
| `DJANGO_ALLOWED_HOSTS` | `.onrender.com,localhost,127.0.0.1` | ✅ Auto |
| `CSRF_TRUSTED_ORIGINS` | `https://*.onrender.com,http://localhost:8000,http://127.0.0.1:8000` | ✅ Auto |
| **`DATABASE_URL`** | `postgresql://postgres:gti9082lduos@db.qjbvlgcmhtdlkqmaxtqx.supabase.co:5432/postgres` | ⚠️ Manual |
| **`SITE_URL`** | `https://cineclubchatarra.onrender.com` | ⚠️ Manual |
| **`GMAIL_USER`** | `cinechatarra911@gmail.com` | ⚠️ Manual |
| **`GMAIL_PASSWORD`** | *(ver Paso 6)* | ⚠️ Manual |
| **`TMDB_API_KEY`** | `2a6b9cd4e128d1f60cd4c461ca187589` | ⚠️ Manual |
| **`TMDB_BEARER_TOKEN`** | `eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyYTZiOWNkNGUxMjhkMWY2MGNkNGM0NjFjYTE4NzU4OSIsIm5iZiI6MTc4Mjg2MzI1OC41ODIsInN1YiI6IjZhNDQ1NTlhYjQzZDM2MDZmZGY4MjQ2YiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.8IkmvGaEhyDmjUJ3Tvgn_zLJnXGA3-S1F0n8XZ2n4M4` | ⚠️ Manual |

**Pasos para agregar variables manuales:**

1. En Render Dashboard, ve a tu servicio → **Environment**
2. Haz clic en **"Add Environment Variable"** (para cada una de las ⚠️ Manual)
3. Pega el valor exacto (sin espacios adicionales)
4. Haz clic en **Save Changes**

> 🔐 **Importante**: `SECRET_KEY` se genera automáticamente (`generateValue: true`). No reemplaces ese valor.

---

### Paso 6: Generar contraseña de aplicación de Google

Para que el envío de correos funcione (Gmail SMTP), necesitas una **contraseña de aplicación** de Google. La contraseña normal de Gmail **NO sirve** porque tienes 2FA activado.

**Requisitos previos**:
- Tener activada la **Verificación en 2 pasos** en tu cuenta de Google
- Usar la cuenta `cinechatarra911@gmail.com`

**Pasos**:

1. Ve a https://myaccount.google.com/security

2. Si **NO** tienes la Verificación en 2 pasos activada:
   - En "Cómo iniciar sesión en Google" → haz clic en **"Verificación en 2 pasos"**
   - Sigue los pasos para activarla (necesitarás tu teléfono)
   - IMPORTANTE: No sigas hasta completar este paso

3. Una vez activada la verificación en 2 pasos:
   - Ve a la misma página de seguridad
   - En "Cómo iniciar sesión en Google" → busca **"Contraseñas de aplicaciones"**
   - Si no lo ves, busca en el buscador de arriba: "contraseñas de aplicaciones"
   - O ve directo a: https://myaccount.google.com/apppasswords

4. En la pantalla de contraseñas de aplicaciones:
   - **Seleccionar aplicación**: Elige "Correo" (o "Mail" en inglés)
   - **Seleccionar dispositivo**: Elige "Otro (nombre personalizado)"
   - **Escribe el nombre**: `cineclubchatarra-render`
   - Haz clic en **"Generar"**

5. Google te mostrará una contraseña de **16 caracteres** con espacios (ej: `abcd efgh ijkl mnop`):
   - **Copia la contraseña INCLUYENDO los espacios** (Render la interpreta igual)
   - **Guárdala inmediatamente**, no podrás verla de nuevo
   - Si pierdes la contraseña, tendrás que generar otra

6. Ve a Render Dashboard → **Environment** → edita `GMAIL_PASSWORD` y pega la contraseña

> ⚠️ **Solución alternativa** (si no quieres usar contraseña de aplicación):
> Puedes configurar **SendGrid** gratis (100 emails/día). Si prefieres esta ruta:
> 1. Regístrate en https://sendgrid.com (plan free: 100 emails/día)
> 2. Crea una API Key con permisos de "Mail Send"
> 3. Configura `SENDGRID_API_KEY` en Render en vez de `GMAIL_USER`/`GMAIL_PASSWORD`
> 4. El código ya soporta SendGrid (líneas 124-130 de settings.py)

---

### Paso 7: Verificar start command

El `render.yaml` ya tiene el start command correcto:

```yaml
startCommand: gunicorn cineclubchatarra.wsgi:application --workers 2 --threads 2 --bind 0.0.0.0:$PORT
```

**Verifica en Render Dashboard** que efectivamente se esté usando:

1. Ve a tu servicio → **Settings**
2. En la sección **"Start Command"**, debe aparecer:
   ```
   gunicorn cineclubchatarra.wsgi:application --workers 2 --threads 2 --bind 0.0.0.0:$PORT
   ```
3. Si ves `gunicorn app:app` o cualquier otra cosa, cámbialo manualmente

> Si usaste Blueprint deploy (Opción A del Paso 3), el start command se toma automáticamente del `render.yaml`. Si no, debes corregirlo manualmente en Settings.

---

### Paso 8: Hacer deploy

Una vez completado todo lo anterior:

1. Ve a tu servicio en Render Dashboard
2. Haz clic en **"Manual Deploy"** → **"Deploy latest commit"**

O alternativamente, haz un push a GitHub (el deploy se gatilla automáticamente si configuraste el Blueprint correctamente):

```powershell
git push origin main
```

**Monitorea los logs del build** en tiempo real. Debes ver:

```
==> Cloning repo...
==> Using Python 3.11.0
==> Running build command: ./build.sh
...
Successfully installed Django-5.1.15 gunicorn-23.0.0 ...
Operations to perform:  Apply all migrations: ...
OK
Successfully populated...
Downloading posters...
0 static files copied...
==> Build successful 🎉
==> Starting service with: gunicorn cineclubchatarra.wsgi:application --workers 2 --threads 2 --bind 0.0.0.0:$PORT
```

**Tiempo estimado de build**: 2-3 minutos (vs. 15+ minutos con easyocr).

---

### Paso 9: Post-deploy — migraciones y datos

El `build.sh` ya ejecuta `migrate`, `poblar_datos --if-empty`, `descargar_posters` y `collectstatic`. Sin embargo, estos comandos dependen de que `DATABASE_URL` esté configurada correctamente (la de Supabase).

Si necesitas ejecutar comandos adicionales en Render (como crear un superusuario), usa **Render Shell**:

1. Ve a tu servicio → **Shell**
2. Ejecuta los comandos:

```bash
# Verificar conexión a BD
python manage.py check --deploy

# Crear superusuario (si no existe)
python manage.py createsuperuser

# Verificar datos
python manage.py shell -c "from core.models import Funcion; print(f'Funciones: {Funcion.objects.count()}'); print(f'Con poster: {Funcion.objects.exclude(poster_path__isnull=True).count()}')"
```

---

## 3. Checklist de Verificación

### 🔲 Pre-deploy (archivos)

| # | Item | Comando para verificar |
|---|------|------------------------|
| 1 | `requirements.txt` sin easyocr/Pillow/unidecode | `cat requirements.txt \| grep -c easyocr` (debe dar 0) |
| 2 | `requirements.txt` con solo las 8 dependencias | `cat requirements.txt \| Measure-Object -Line` (debe dar 8 líneas) |
| 3 | `runtime.txt` existe con `python-3.11.0` | `cat runtime.txt` |
| 4 | `build.sh` existe y es ejecutable | `Test-Path build.sh` |
| 5 | `render.yaml` tiene start command correcto | Ver contenido: `gunicorn cineclubchatarra.wsgi...` |
| 6 | Último commit pusheado a GitHub | `git log -1 --oneline` → debe mostrar el commit de la limpieza |

### 🔲 Deploy en Render

| # | Item | Cómo verificarlo |
|---|------|------------------|
| 7 | Blueprint deploy (no manual) | Dashboard debe mostrar "Blueprint" en la info del servicio |
| 8 | Python 3.11.0 usado | Log de build: buscar "Using Python 3.11.0" |
| 9 | Build exitoso | Log termina con "Build successful 🎉" |
| 10 | Start command correcto | Settings → Start Command → debe ser `gunicorn cineclubchatarra.wsgi...` |

### 🔲 Variables de entorno en Render

| # | Variable | Verificar |
|---|----------|-----------|
| 11 | `DATABASE_URL` | Configurada con la URL de Supabase |
| 12 | `SITE_URL` | `https://cineclubchatarra.onrender.com` |
| 13 | `GMAIL_USER` | `cinechatarra911@gmail.com` |
| 14 | `GMAIL_PASSWORD` | Contraseña de 16 caracteres generada en Google |
| 15 | `TMDB_API_KEY` | `2a6b9cd4e128d1f60cd4c461ca187589` |
| 16 | `TMDB_BEARER_TOKEN` | Token completo (string largo que empieza con `eyJhbGci...`) |
| 17 | `SECRET_KEY` | Generada automáticamente por Render (no tocar) |
| 18 | `DEBUG` | `False` |
| 19 | `DJANGO_ALLOWED_HOSTS` | `.onrender.com,localhost,127.0.0.1` |

### 🔲 Post-deploy (funcionamiento)

| # | Item | Cómo verificarlo |
|---|------|------------------|
| 20 | App responde en HTTPS | Abrir `https://cineclubchatarra.onrender.com` |
| 21 | Página de feed carga sin errores | Verificar que se vea el layout y funciones |
| 22 | Admin funciona | Ir a `https://cineclubchatarra.onrender.com/admin/` |
| 23 | Estáticos cargan (CSS/JS) | Abrir DevTools → Network → buscar `.css` y `.js` servidos |
| 24 | Posters se ven | Verificar que las imágenes de películas carguen |
| 25 | Base de datos conectada | Los datos de funciones/ciclos deben aparecer (no vacío) |
| 26 | Migraciones aplicadas | `python manage.py showmigrations` en Shell de Render → todos `[X]` |
| 27 | `DEFAULT_FROM_EMAIL` | Configurado como `cinechatarra911@gmail.com` (default en settings.py) |

### 🔲 Si algo falla

| Síntoma | Causa probable | Solución |
|---------|----------------|----------|
| Build falla con timeout | easyocr aún en requirements.txt | Volver al Paso 1 |
| Build usa Python 3.14 | No usaste Blueprint deploy | Volver al Paso 3 (Opción B) |
| App no arranca | Start command incorrecto | Ir a Settings → corregir manualmente |
| "DisallowedHost" error | `DJANGO_ALLOWED_HOSTS` mal configurado | Agregar `.onrender.com` |
| "Connection refused" DB | `DATABASE_URL` incorrecta o Supabase caído | Verificar URL en Supabase Dashboard |
| Página sin estilos | `collectstatic` no corrió o error en WhiteNoise | Ejecutar `python manage.py collectstatic --noinput` en Shell |
| "Please log in via your web browser" (email) | GMAIL_PASSWORD incorrecta o contraseña de app mal generada | Regenerar en https://myaccount.google.com/apppasswords |
| 502 Bad Gateway | Workers de gunicorn insuficientes o app crashea | Revisar logs en Render Dashboard |
| Funciones sin poster | `descargar_posters` no encontró TMDB o falló | Ejecutar manualmente `python manage.py descargar_posters` en Shell |

---

## 4. Referencias

### Archivos del proyecto

| Archivo | Propósito |
|---------|-----------|
| `requirements.txt` | Dependencias de Python (producción) |
| `runtime.txt` | Versión de Python para Render/Heroku |
| `render.yaml` | Configuración de infraestructura para Render Blueprint |
| `build.sh` | Script de build ejecutado en Render |
| `cineclubchatarra/settings.py` | Configuración principal de Django |
| `.env` | Variables locales (NO subir a GitHub — está en `.gitignore`) |
| `core/management/commands/importar_posters_instagram.py` | Comando local para importar posters desde Instagram |

### URLs útiles

| Recurso | URL |
|---------|-----|
| Render Dashboard | https://dashboard.render.com |
| Supabase Dashboard | https://supabase.com/dashboard |
| Contraseñas de aplicación Google | https://myaccount.google.com/apppasswords |
| Token personal GitHub | https://github.com/settings/tokens |
| Repositorio del proyecto | https://github.com/gambito700/cineclubchatarra |
| SendGrid (alternativa email) | https://sendgrid.com |

### Notas finales

- **easyocr, Pillow y unidecode** se eliminaron de requirements.txt. Si necesitas ejecutar `importar_posters_instagram` desde tu máquina local, instala esas dependencias manualmente: `pip install easyocr==1.7.2 Pillow==11.1.0 unidecode==1.3.8`
- Si algún miembro del equipo clona el repo y ejecuta `pip install -r requirements.txt`, **no tendrá easyocr/Pillow/unidecode**. Si necesita usarlos, que los instale por separado. Considera crear un archivo `requirements-local.txt` para dependencias de desarrollo si se vuelve recurrente.
- La app usa `URLField` para posters (no `ImageField`), por lo que Django no necesita Pillow para producción.
- `unidecode` era una dependencia fantasma: nunca se importó en ningún archivo del proyecto.

---

> **Hecho por**: AgentsOrchestrator — Pipeline de deploy automatizado  
> **Última actualización**: 30 de junio de 2026
