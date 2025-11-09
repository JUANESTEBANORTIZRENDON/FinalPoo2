"""
Registro de modelos en el AdminSite personalizado
"""
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from .admin_site import admin_site


# Registrar User con el UserAdmin por defecto de Django
admin_site.register(User, UserAdmin)

# Registrar Group con el GroupAdmin por defecto de Django
admin_site.register(Group, GroupAdmin)
