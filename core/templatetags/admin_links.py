"""
Template tags para enlaces seguros del admin
Evita errores NoReverseMatch cuando no existen rutas
"""
from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()


@register.simple_tag(takes_context=True)
def admin_url(context, app_model, action='changelist'):
    """
    Resuelve URLs del admin de forma segura, retornando cadena vacía si no existe
    
    Uso en templates:
        {% load admin_links %}
        {% admin_url 'auth_user' 'changelist' as user_list_url %}
        {% if user_list_url %}
            <a href="{{ user_list_url }}">Ver usuarios</a>
        {% endif %}
    
    Args:
        context: Contexto del template (automático)
        app_model: Nombre del modelo en formato 'app_model' (ej: 'auth_user', 'auth_group')
        action: Acción del admin ('changelist', 'add', 'change', 'delete', 'history')
    
    Returns:
        str: URL resuelta o cadena vacía si no existe
    """
    # Obtener el namespace del admin actual (debe ser 'admin')
    request = context.get('request')
    current_app = getattr(request, 'current_app', 'admin')
    
    # Construir el nombre de la URL
    url_name = f'{current_app}:{app_model}_{action}'
    
    try:
        return reverse(url_name)
    except NoReverseMatch:
        # Silenciosamente retornar cadena vacía si la URL no existe
        return ''


@register.simple_tag(takes_context=True)
def safe_admin_url(context, app_label, model_name, action='changelist', object_id=None):
    """
    Versión alternativa más flexible para construir URLs del admin
    
    Uso:
        {% safe_admin_url 'auth' 'user' 'changelist' as user_list %}
        {% safe_admin_url 'auth' 'user' 'change' object.pk as user_change %}
    
    Args:
        context: Contexto del template
        app_label: Etiqueta de la app (ej: 'auth', 'empresas')
        model_name: Nombre del modelo (ej: 'user', 'group')
        action: Acción (changelist, add, change, delete, history)
        object_id: ID del objeto (requerido para change, delete, history)
    
    Returns:
        str: URL o cadena vacía
    """
    request = context.get('request')
    current_app = getattr(request, 'current_app', 'admin')
    
    # Construir el nombre de la URL
    url_name = f'{current_app}:{app_label}_{model_name}_{action}'
    
    try:
        if object_id and action in ['change', 'delete', 'history']:
            return reverse(url_name, args=[object_id])
        else:
            return reverse(url_name)
    except NoReverseMatch:
        return ''


@register.simple_tag
def has_admin_url(app_model, action='changelist'):
    """
    Verifica si existe una URL del admin sin intentar resolverla
    
    Uso:
        {% has_admin_url 'auth_user' 'changelist' as has_user_list %}
        {% if has_user_list %}
            <!-- Mostrar contenido -->
        {% endif %}
    
    Returns:
        bool: True si la URL existe, False si no
    """
    url_name = f'admin:{app_model}_{action}'
    
    try:
        reverse(url_name)
        return True
    except NoReverseMatch:
        return False


@register.filter
def admin_model_url(model_instance, action='change'):
    """
    Genera URL del admin para una instancia de modelo
    
    Uso en templates:
        {{ object|admin_model_url:'change' }}
        {{ object|admin_model_url:'delete' }}
    
    Args:
        model_instance: Instancia del modelo
        action: Acción (change, delete, history)
    
    Returns:
        str: URL o cadena vacía
    """
    if not model_instance or not hasattr(model_instance, '_meta'):
        return ''
    
    opts = model_instance._meta
    app_label = opts.app_label
    model_name = opts.model_name
    
    url_name = f'admin:{app_label}_{model_name}_{action}'
    
    try:
        return reverse(url_name, args=[model_instance.pk])
    except NoReverseMatch:
        return ''
