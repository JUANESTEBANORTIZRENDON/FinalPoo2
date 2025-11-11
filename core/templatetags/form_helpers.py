"""
Template tags personalizados para renderizar formularios Django
con Bootstrap 5 y reducir duplicación de código.
"""
from django import template

register = template.Library()


@register.inclusion_tag('components/form_field.html')
def render_field(field, show_label=True, label_class='form-label', field_class='form-control', help_text=None):
    """
    Renderiza un campo de formulario Django con Bootstrap 5.
    
    Args:
        field: Campo del formulario Django
        show_label: Mostrar o no el label
        label_class: Clases CSS para el label
        field_class: Clases CSS para el campo
        help_text: Texto de ayuda personalizado
        
    Returns:
        Context para el template
    """
    # Agregar clases Bootstrap al campo
    if field.field.widget.__class__.__name__ == 'CheckboxInput':
        field.field.widget.attrs['class'] = 'form-check-input'
    else:
        existing_classes = field.field.widget.attrs.get('class', '')
        field.field.widget.attrs['class'] = f'{existing_classes} {field_class}'.strip()
    
    return {
        'field': field,
        'show_label': show_label,
        'label_class': label_class,
        'help_text': help_text or field.help_text,
        'is_required': field.field.required,
    }


@register.inclusion_tag('components/form_errors.html')
def render_form_errors(form):
    """
    Renderiza errores generales del formulario en un alert de Bootstrap.
    
    Args:
        form: Formulario Django
        
    Returns:
        Context con errores
    """
    errors = []
    
    # Errores de campos
    for field in form:
        if field.errors:
            for error in field.errors:
                errors.append(f"{field.label}: {error}")
    
    # Errores no asociados a campos
    if form.non_field_errors():
        errors.extend(form.non_field_errors())
    
    return {
        'errors': errors,
        'has_errors': bool(errors),
    }


@register.filter
def add_class(field, css_class):
    """
    Agrega clases CSS a un campo de formulario.
    
    Usage: {{ form.field|add_class:"form-control" }}
    """
    existing_classes = field.field.widget.attrs.get('class', '')
    field.field.widget.attrs['class'] = f'{existing_classes} {css_class}'.strip()
    return field


@register.filter
def is_checkbox(field):
    """
    Verifica si un campo es un checkbox.
    """
    return field.field.widget.__class__.__name__ == 'CheckboxInput'
