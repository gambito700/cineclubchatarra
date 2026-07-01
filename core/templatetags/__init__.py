# Template tags personalizados para Cine Chatarra
from django import template

register = template.Library()


@register.filter
def modulo(value, arg):
    """Filtro de módulo: {{ value|modulo:28 }}"""
    try:
        return int(value) % int(arg)
    except (ValueError, ZeroDivisionError):
        return 0


@register.filter
def grad_class(value):
    """Convierte un número a clase de gradiente,
    ciclando entre 1 y 28."""
    try:
        return (int(value) % 28) + 1
    except ValueError:
        return 1
