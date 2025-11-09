from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='sum_attr')
def sum_attr(queryset, attr_name):
    """
    Suma un atributo específico de todos los objetos en un queryset.
    Uso: {{ object_list|sum_attr:"valor" }}
    """
    try:
        total = sum(getattr(obj, attr_name, 0) for obj in queryset)
        return total
    except (TypeError, AttributeError):
        return 0

@register.filter(name='filter_by_estado')
def filter_by_estado(queryset, estado):
    """
    Filtra un queryset por estado.
    Uso: {{ object_list|filter_by_estado:"pendiente" }}
    """
    try:
        return [obj for obj in queryset if obj.estado == estado]
    except AttributeError:
        return []

@register.filter(name='count_by_estado')
def count_by_estado(queryset, estado):
    """
    Cuenta cuántos objetos tienen un estado específico.
    Uso: {{ object_list|count_by_estado:"pendiente" }}
    """
    try:
        return len([obj for obj in queryset if obj.estado == estado])
    except AttributeError:
        return 0
