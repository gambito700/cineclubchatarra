# Modelos de datos para Cine Chatarra
from django.db import models
from django.utils.text import slugify
from django.conf import settings

# ═══════════════════════════════════════════
#  CICLO — Agrupa funciones por temática/mes
# ═══════════════════════════════════════════
class Ciclo(models.Model):
    """Ciclo temático de cine (ej: "Julio del Terror", "Aki Kaurismäki")"""
    nombre = models.CharField(max_length=200, verbose_name="Nombre del ciclo")
    slug = models.SlugField(unique=True, blank=True, verbose_name="URL amigable")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    fecha_inicio = models.DateField(null=True, blank=True, verbose_name="Fecha inicio")
    fecha_fin = models.DateField(null=True, blank=True, verbose_name="Fecha fin")
    orden = models.IntegerField(default=0, help_text="Orden cronológico (menor = más antiguo)")
    es_especial = models.BooleanField(default=False, verbose_name="¿Es evento especial?")
    created_at = models.DateTimeField(auto_now_add=True)

    imagen_path = models.URLField(max_length=500, null=True, blank=True,
                                   verbose_name="URL de imagen del ciclo")

    class Meta:
        ordering = ['orden']
        verbose_name = 'Ciclo'
        verbose_name_plural = 'Ciclos'

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.nombre)
            slug = base
            contador = 1
            while Ciclo.objects.filter(slug=slug).exists():
                slug = f"{base}-{contador}"
                contador += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

# ═══════════════════════════════════════════
#  FUNCIÓN — Cada proyección individual
# ═══════════════════════════════════════════
class Funcion(models.Model):
    """Una función/película proyectada por el cine club"""
    titulo_pelicula = models.CharField(max_length=300, verbose_name="Título de la película")
    director = models.CharField(max_length=300, blank=True, verbose_name="Director/a")
    año = models.CharField(max_length=20, blank=True, verbose_name="Año de estreno")
    pais = models.CharField(max_length=200, blank=True, verbose_name="País de origen")
    # La fecha puede ser precisa (DateField) o aproximada (CharField)
    fecha_funcion = models.CharField(max_length=100, blank=True, verbose_name="Fecha de función (texto)")
    fecha_precisa = models.DateField(null=True, blank=True, verbose_name="Fecha exacta (si se conoce)")
    hora = models.CharField(max_length=50, blank=True, verbose_name="Horario")
    locacion = models.CharField(max_length=300, blank=True, verbose_name="Lugar de proyección")
    tipo = models.CharField(max_length=50, blank=True, verbose_name="Tipo (largometraje/corto/documental/animación)")
    ciclo = models.ForeignKey(Ciclo, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='funciones', verbose_name="Ciclo al que pertenece")
    sinopsis = models.TextField(blank=True, verbose_name="Sinopsis / descripción")
    orden = models.IntegerField(default=0, help_text="Orden dentro del ciclo")
    poster_path = models.URLField(max_length=500, null=True, blank=True,
                                   verbose_name="URL del poster (TMDB)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ciclo__orden', 'orden']
        verbose_name = 'Función'
        verbose_name_plural = 'Funciones'

    def __str__(self):
        ciclo = f" [{self.ciclo.nombre}]" if self.ciclo else ""
        return f"{self.titulo_pelicula}{ciclo}"

# ═══════════════════════════════════════════
#  LOCACIÓN — Lugares donde ha proyectado
# ═══════════════════════════════════════════
class Locacion(models.Model):
    """Locación física donde el club ha proyectado películas"""
    nombre = models.CharField(max_length=200, verbose_name="Nombre del lugar")
    direccion = models.CharField(max_length=300, blank=True, verbose_name="Dirección")
    periodo_inicio = models.CharField(max_length=100, blank=True, verbose_name="Período inicio")
    periodo_fin = models.CharField(max_length=100, blank=True, verbose_name="Período fin")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    orden = models.IntegerField(default=0, help_text="Orden cronológico")

    class Meta:
        ordering = ['orden']
        verbose_name = 'Locación'
        verbose_name_plural = 'Locaciones'

    def __str__(self):
        return self.nombre

# ═══════════════════════════════════════════
#  EVENTO ESPECIAL — Actividades extras
# ═══════════════════════════════════════════
class EventoEspecial(models.Model):
    """Evento que no es una función regular (completadas, lanzamientos, etc.)"""
    titulo = models.CharField(max_length=300, verbose_name="Título del evento")
    fecha = models.CharField(max_length=100, blank=True, verbose_name="Fecha")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    funcion = models.ForeignKey(Funcion, on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name="Función relacionada")

    class Meta:
        ordering = ['fecha']
        verbose_name = 'Evento especial'
        verbose_name_plural = 'Eventos especiales'

    def __str__(self):
        return self.titulo


# ═══════════════════════════════════════════
#  AVISO — Notificaciones para la comunidad
# ═══════════════════════════════════════════
class Aviso(models.Model):
    """Aviso que aparece como banner en el feed + opcional email"""
    titulo = models.CharField(max_length=200, verbose_name="Título del aviso")
    mensaje = models.TextField(verbose_name="Mensaje")
    funcion = models.ForeignKey(Funcion, on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name="Función relacionada")
    es_urgente = models.BooleanField(default=False, verbose_name="¿Es urgente?")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Aviso'
        verbose_name_plural = 'Avisos'

    def __str__(self):
        return self.titulo


# ═══════════════════════════════════════════
#  SUSCRIPTOR — Personas que reciben avisos
# ═══════════════════════════════════════════
class Suscriptor(models.Model):
    email = models.EmailField(unique=True, verbose_name="Correo electrónico")
    fecha_alta = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True, verbose_name="Activo")
    token_baja = models.CharField(max_length=64, blank=True, verbose_name="Token para darse de baja")

    class Meta:
        verbose_name = 'Suscriptor'
        verbose_name_plural = 'Suscriptores'

    def __str__(self):
        return self.email


# ═══════════════════════════════════════════
#  ENVÍO AVISO — Registro de envíos de email
# ═══════════════════════════════════════════
class EnvioAviso(models.Model):
    """Registro de cada envío de aviso por email"""
    aviso = models.ForeignKey(Aviso, on_delete=models.CASCADE, related_name='envios')
    fecha_envio = models.DateTimeField(auto_now_add=True)
    destinatarios_count = models.IntegerField(default=0, verbose_name="Cantidad de destinatarios")

    class Meta:
        verbose_name = 'Envío de aviso'
        verbose_name_plural = 'Envíos de avisos'

    def __str__(self):
        return f"{self.aviso.titulo} — {self.fecha_envio.strftime('%d/%m/%Y %H:%M')}"


# ═══════════════════════════════════════════
#  ENCUESTA — Votación participativa
# ═══════════════════════════════════════════
class Encuesta(models.Model):
    """Encuesta para votar por películas, ciclos, etc."""
    titulo = models.CharField(max_length=200, verbose_name="Título")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    activa = models.BooleanField(default=True, verbose_name="Activa")
    fecha_cierre = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de cierre")
    mostrar_resultados = models.BooleanField(default=True, verbose_name="Mostrar resultados")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Encuesta'
        verbose_name_plural = 'Encuestas'

    def __str__(self):
        return self.titulo


class OpcionEncuesta(models.Model):
    """Opción individual dentro de una encuesta"""
    encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE, related_name='opciones')
    texto = models.CharField(max_length=300, verbose_name="Texto de la opción")
    orden = models.IntegerField(default=0, verbose_name="Orden")

    class Meta:
        ordering = ['orden']
        verbose_name = 'Opción de encuesta'
        verbose_name_plural = 'Opciones de encuesta'

    def __str__(self):
        return self.texto


class Voto(models.Model):
    """Voto de un usuario en una encuesta"""
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    opcion = models.ForeignKey(OpcionEncuesta, on_delete=models.CASCADE)
    encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['usuario', 'encuesta'], name='un_voto_por_encuesta')
        ]
        verbose_name = 'Voto'
        verbose_name_plural = 'Votos'

    def __str__(self):
        return f"{self.usuario.username} → {self.opcion.texto}"


# ═══════════════════════════════════════════
#  PATROCINADOR — Sponsors del cine club
# ═══════════════════════════════════════════
class Patrocinador(models.Model):
    """Entidad patrocinadora del cine club"""
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    logo_url = models.URLField(max_length=500, blank=True, verbose_name="URL del logo")
    sitio_web = models.URLField(max_length=500, blank=True, verbose_name="Sitio web")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    orden = models.IntegerField(default=0, verbose_name="Orden")

    class Meta:
        ordering = ['orden']
        verbose_name = 'Patrocinador'
        verbose_name_plural = 'Patrocinadores'

    def __str__(self):
        return self.nombre


# ═══════════════════════════════════════════
#  ASISTENCIA — Check-in "Yo estuve ahí"
# ═══════════════════════════════════════════
class Asistencia(models.Model):
    """Registro de que un usuario asistió a una función"""
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    funcion = models.ForeignKey(Funcion, on_delete=models.CASCADE, related_name='asistencias')
    fecha_checkin = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['usuario', 'funcion'], name='un_checkin_por_funcion')
        ]
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'

    def __str__(self):
        return f"{self.usuario.username} → {self.funcion.titulo_pelicula}"


# ═══════════════════════════════════════════
#  RECAUDACIÓN — Donaciones del público
# ═══════════════════════════════════════════
class Recaudacion(models.Model):
    """Registro de donaciones recibidas durante las funciones"""
    concepto = models.CharField(max_length=200, verbose_name="Concepto")
    monto = models.IntegerField(verbose_name="Monto (CLP)")
    funcion = models.ForeignKey(Funcion, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='recaudaciones', verbose_name="Función")
    donante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                 null=True, blank=True, verbose_name="Donante")
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Recaudación'
        verbose_name_plural = 'Recaudaciones'

    def __str__(self):
        return f"${self.monto:,} — {self.concepto}"
