# Panel de administración Django para Cine Chatarra
from django.contrib import admin
from django.utils.html import format_html
from .models import (Ciclo, Funcion, Locacion, EventoEspecial,
                     Aviso, Suscriptor, EnvioAviso,
                     Encuesta, OpcionEncuesta, Voto,
                     Patrocinador, Asistencia, Recaudacion)
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages


# ─── CICLO ───
@admin.register(Ciclo)
class CicloAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'orden', 'fecha_inicio', 'es_especial', 'preview_imagen']
    prepopulated_fields = {'slug': ['nombre']}
    search_fields = ['nombre']

    def preview_imagen(self, obj):
        if obj.imagen_path:
            return format_html('<img src="{}" style="height:40px;border-radius:4px;">', obj.imagen_path)
        return '—'
    preview_imagen.short_description = 'Imagen'


# ─── FUNCIÓN ───
@admin.register(Funcion)
class FuncionAdmin(admin.ModelAdmin):
    list_display = ['titulo_pelicula', 'director', 'año', 'ciclo', 'fecha_funcion', 'preview_poster']
    list_filter = ['ciclo', 'tipo', 'pais']
    search_fields = ['titulo_pelicula', 'director']

    def preview_poster(self, obj):
        if obj.poster_path:
            return format_html('<img src="{}" style="height:40px;border-radius:4px;">', obj.poster_path)
        return '—'
    preview_poster.short_description = 'Poster'


# ─── LOCACIÓN ───
@admin.register(Locacion)
class LocacionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'direccion', 'periodo_inicio', 'periodo_fin']


# ─── EVENTO ESPECIAL ───
@admin.register(EventoEspecial)
class EventoEspecialAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'fecha']


# ─── AVISO ───
class EnvioAvisoInline(admin.TabularInline):
    model = EnvioAviso
    readonly_fields = ['fecha_envio', 'destinatarios_count']
    extra = 0
    can_delete = False

@admin.register(Aviso)
class AvisoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'activo', 'es_urgente', 'created_at']
    list_filter = ['activo', 'es_urgente']
    actions = ['enviar_aviso_por_email']
    inlines = [EnvioAvisoInline]

    @admin.action(description='Enviar este aviso por email a suscriptores')
    def enviar_aviso_por_email(self, request, queryset):
        for aviso in queryset:
            suscriptores = Suscriptor.objects.filter(activo=True)
            if not suscriptores.exists():
                self.message_user(request, f'No hay suscriptores activos para "{aviso.titulo}".', level='WARNING')
                continue
            enviado = 0
            for sub in suscriptores:
                try:
                    send_mail(
                        subject=f'[Cine Chatarra] {aviso.titulo}',
                        message=f'{aviso.mensaje}\n\n---\nCine Club Chatarra\nPara darte de baja: {settings.SITE_URL}/suscriptores/baja/{sub.token_baja}/',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[sub.email],
                        fail_silently=True,
                    )
                    enviado += 1
                except Exception:
                    pass
            EnvioAviso.objects.create(aviso=aviso, destinatarios_count=enviado)
            self.message_user(request, f'"{aviso.titulo}" enviado a {enviado} suscriptores.')
        enviar_aviso_por_email.short_description = 'Enviar aviso por email'


# ─── SUSCRIPTOR ───
@admin.register(Suscriptor)
class SuscriptorAdmin(admin.ModelAdmin):
    list_display = ['email', 'activo', 'fecha_alta']
    list_filter = ['activo']
    search_fields = ['email']


# ─── ENVÍO AVISO ───
@admin.register(EnvioAviso)
class EnvioAvisoAdmin(admin.ModelAdmin):
    list_display = ['aviso', 'fecha_envio', 'destinatarios_count']
    readonly_fields = ['fecha_envio', 'destinatarios_count']


# ─── ENCUESTA ───
class OpcionEncuestaInline(admin.TabularInline):
    model = OpcionEncuesta
    extra = 2
    fields = ['texto', 'orden']

@admin.register(Encuesta)
class EncuestaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'activa', 'fecha_cierre', 'total_votos']
    list_filter = ['activa']
    inlines = [OpcionEncuestaInline]

    def total_votos(self, obj):
        return Voto.objects.filter(encuesta=obj).count()
    total_votos.short_description = 'Votos'


@admin.register(OpcionEncuesta)
class OpcionEncuestaAdmin(admin.ModelAdmin):
    list_display = ['texto', 'encuesta', 'orden', 'conteo_votos']
    list_filter = ['encuesta']

    def conteo_votos(self, obj):
        return obj.voto_set.count()
    conteo_votos.short_description = 'Votos'


@admin.register(Voto)
class VotoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'encuesta', 'opcion', 'fecha']
    list_filter = ['encuesta']


# ─── PATROCINADOR ───
@admin.register(Patrocinador)
class PatrocinadorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo', 'orden', 'preview_logo']
    list_filter = ['activo']

    def preview_logo(self, obj):
        if obj.logo_url:
            return format_html('<img src="{}" style="height:30px;border-radius:4px;">', obj.logo_url)
        return '—'
    preview_logo.short_description = 'Logo'


# ─── ASISTENCIA ───
@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'funcion', 'fecha_checkin']
    list_filter = ['funcion__ciclo']
    search_fields = ['usuario__username', 'funcion__titulo_pelicula']


# ─── RECAUDACIÓN ───
@admin.register(Recaudacion)
class RecaudacionAdmin(admin.ModelAdmin):
    list_display = ['concepto', 'monto_formateado', 'funcion', 'fecha']
    list_filter = ['funcion__ciclo']

    def monto_formateado(self, obj):
        return f"${obj.monto:,}"
    monto_formateado.short_description = 'Monto'
