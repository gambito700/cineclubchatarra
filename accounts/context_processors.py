def rol_usuario(request):
    if request.user.is_authenticated:
        return {
            'es_admin': request.user.rol == 'admin',
            'es_patrocinador': request.user.rol == 'patrocinador',
            'es_aficionado': request.user.rol == 'aficionado',
            'rol_usuario': request.user.rol,
        }
    return {
        'es_admin': False,
        'es_patrocinador': False,
        'es_aficionado': False,
        'rol_usuario': 'visitante',
    }
