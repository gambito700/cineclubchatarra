from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def si_rol(context, *roles):
    request = context.get('request')
    if request and request.user.is_authenticated:
        return request.user.rol in roles
    return 'visitante' in roles
