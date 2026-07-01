from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Debes iniciar sesión para acceder.')
            return redirect('accounts:login')
        if request.user.rol != 'admin':
            messages.error(request, 'No tienes permisos de administrador.')
            return redirect('core:feed')
        return view_func(request, *args, **kwargs)
    return _wrapped


def patrocinador_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Debes iniciar sesión para acceder.')
            return redirect('accounts:login')
        if request.user.rol not in ('patrocinador', 'admin'):
            messages.error(request, 'Solo patrocinadores pueden acceder a esta sección.')
            return redirect('core:feed')
        return view_func(request, *args, **kwargs)
    return _wrapped
