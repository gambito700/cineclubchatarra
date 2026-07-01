# Vistas (controladores) de Cine Chatarra
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.views.decorators.http import require_POST
from .models import (Ciclo, Funcion, Locacion, EventoEspecial,
                     Aviso, Encuesta, OpcionEncuesta, Voto,
                     Patrocinador, Asistencia, Suscriptor, Recaudacion)
from accounts.decorators import admin_required, patrocinador_required
import secrets


# ═══════════════════════════════════════════
#  FEED PRINCIPAL — Tipo Instagram
# ═══════════════════════════════════════════
def feed(request):
    """Página principal: feed tipo Instagram con avisos y encuestas activas"""
    ciclos = Ciclo.objects.filter(es_especial=False)
    funciones = Funcion.objects.select_related('ciclo').all()
    avisos_activos = Aviso.objects.filter(activo=True)
    encuesta_activa = Encuesta.objects.filter(activa=True).first()
    return render(request, 'core/feed.html', {
        'funciones': funciones,
        'ciclos': ciclos,
        'total_funciones': funciones.count(),
        'total_ciclos': ciclos.count(),
        'avisos_activos': avisos_activos,
        'encuesta_activa': encuesta_activa,
    })


# ═══════════════════════════════════════════
#  DETALLE DE CICLO
# ═══════════════════════════════════════════
def detalle_ciclo(request, slug):
    ciclo = get_object_or_404(Ciclo, slug=slug)
    funciones = ciclo.funciones.select_related('ciclo').all()
    return render(request, 'core/ciclo_detalle.html', {
        'ciclo': ciclo,
        'funciones': funciones,
    })


# ═══════════════════════════════════════════
#  DETALLE DE FUNCIÓN
# ═══════════════════════════════════════════
def detalle_funcion(request, pk):
    funcion = get_object_or_404(Funcion, pk=pk)
    ya_asistio = False
    total_asistencias = funcion.asistencias.count()
    if request.user.is_authenticated:
        ya_asistio = Asistencia.objects.filter(usuario=request.user, funcion=funcion).exists()
    if request.GET.get('formato') == 'modal':
        html = render_to_string('core/funcion_modal.html', {
            'funcion': funcion,
            'ya_asistio': ya_asistio,
            'total_asistencias': total_asistencias,
        })
        return HttpResponse(html)
    return render(request, 'core/funcion_detalle.html', {
        'funcion': funcion,
        'ya_asistio': ya_asistio,
        'total_asistencias': total_asistencias,
    })


# ═══════════════════════════════════════════
#  LÍNEA DE TIEMPO
# ═══════════════════════════════════════════
def linea_tiempo(request):
    ciclos = Ciclo.objects.all().prefetch_related('funciones')
    return render(request, 'core/linea_tiempo.html', {
        'ciclos': ciclos,
    })


# ═══════════════════════════════════════════
#  ACERCA DE
# ═══════════════════════════════════════════
def acerca_de(request):
    locaciones = Locacion.objects.all()
    eventos = EventoEspecial.objects.all()
    stats = {
        'total_funciones': Funcion.objects.count(),
        'total_ciclos': Ciclo.objects.count(),
        'total_eventos': eventos.count(),
        'total_locaciones': locaciones.count(),
        'total_directores': Funcion.objects.exclude(director='').values('director').distinct().count(),
        'total_paises': Funcion.objects.exclude(pais='').values('pais').distinct().count(),
    }
    return render(request, 'core/acerca_de.html', {
        'locaciones': locaciones,
        'eventos': eventos,
        'stats': stats,
    })


# ═══════════════════════════════════════════
#  AVISOS — Banner + página de historial
# ═══════════════════════════════════════════
def avisos_lista(request):
    todos = Aviso.objects.all()
    return render(request, 'core/avisos.html', {'avisos': todos})


# ═══════════════════════════════════════════
#  SUSCRIPCIÓN — Formulario público
# ═══════════════════════════════════════════
def suscribir(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            obj, created = Suscriptor.objects.get_or_create(email=email, defaults={
                'token_baja': secrets.token_urlsafe(32),
            })
            if created:
                messages.success(request, '¡Gracias por suscribirte a los avisos!')
            else:
                if not obj.activo:
                    obj.activo = True
                    obj.token_baja = secrets.token_urlsafe(32)
                    obj.save()
                    messages.success(request, '¡Suscripción reactivada!')
                else:
                    messages.info(request, 'Ya estás suscripta/o.')
        else:
            messages.error(request, 'Ingresa un email válido.')
    return redirect('core:feed')


# ═══════════════════════════════════════════
#  ENCUESTAS — Votación participativa
# ═══════════════════════════════════════════
def encuestas_lista(request):
    encuestas = Encuesta.objects.annotate(total_votos=Count('voto'))
    return render(request, 'core/encuesta_lista.html', {'encuestas': encuestas})


def encuesta_detalle(request, pk):
    encuesta = get_object_or_404(Encuesta.objects.annotate(total_votos=Count('voto')), pk=pk)
    ya_voto = False
    voto_usuario = None
    if request.user.is_authenticated:
        voto_usuario = Voto.objects.filter(usuario=request.user, encuesta=encuesta).first()
        ya_voto = voto_usuario is not None

    if request.method == 'POST' and request.user.is_authenticated and not ya_voto and encuesta.activa:
        opcion_id = request.POST.get('opcion')
        opcion = get_object_or_404(OpcionEncuesta, pk=opcion_id, encuesta=encuesta)
        Voto.objects.create(usuario=request.user, opcion=opcion, encuesta=encuesta)
        messages.success(request, '¡Voto registrado!')
        return redirect('core:encuesta_detalle', pk=encuesta.pk)

    return render(request, 'core/encuesta_detalle.html', {
        'encuesta': encuesta,
        'ya_voto': ya_voto,
        'voto_usuario': voto_usuario,
    })


# ═══════════════════════════════════════════
#  PATROCINADORES — Página pública
# ═══════════════════════════════════════════
def patrocinadores_lista(request):
    sponsors = Patrocinador.objects.filter(activo=True)
    return render(request, 'core/patrocinadores.html', {'sponsors': sponsors})


# ═══════════════════════════════════════════
#  SALA PATROCINADORES — Exclusiva
# ═══════════════════════════════════════════
@patrocinador_required
def sala_patrocinadores(request):
    return render(request, 'core/sala_patrocinadores.html')


# ═══════════════════════════════════════════
#  CHECK-IN — "Yo estuve ahí"
# ═══════════════════════════════════════════
@login_required
@require_POST
def checkin(request, funcion_pk):
    funcion = get_object_or_404(Funcion, pk=funcion_pk)
    obj, created = Asistencia.objects.get_or_create(
        usuario=request.user, funcion=funcion
    )
    if created:
        messages.success(request, f'¡Registrado! Estuviste en {funcion.titulo_pelicula}')
    else:
        messages.info(request, 'Ya registraste tu asistencia a esta función.')
    return redirect(request.META.get('HTTP_REFERER', 'core:feed'))


# ═══════════════════════════════════════════
#  PERFIL — Historial del usuario
# ═══════════════════════════════════════════
@login_required
def perfil(request, username=None):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if username:
        usuario = get_object_or_404(User, username=username)
    else:
        usuario = request.user
    asistencias = Asistencia.objects.filter(usuario=usuario).select_related('funcion')
    return render(request, 'core/perfil.html', {
        'usuario_perfil': usuario,
        'asistencias': asistencias,
    })


def baja_suscripcion(request, token):
    suscriptor = get_object_or_404(Suscriptor, token_baja=token)
    suscriptor.activo = False
    suscriptor.save()
    messages.success(request, 'Te has dado de baja de los avisos. Si cambias de opinión, puedes volver a suscribirte desde el feed.')
    return redirect('core:feed')
