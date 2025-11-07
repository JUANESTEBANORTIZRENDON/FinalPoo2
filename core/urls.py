"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.shortcuts import redirect
from django.http import HttpResponse
from django.views.decorators.http import require_safe

@require_safe
def home_view(request):
    """Vista de inicio que redirige según el estado de autenticación"""
    if request.user.is_authenticated:
        # Redirigir al dashboard del holding según el rol
        return redirect('/empresas/admin/dashboard/')
    else:
        return redirect('/accounts/login/')
 
 #Holi
urlpatterns = [
    # ===== ADMINISTRACIÓN =====
    path('admin/', admin.site.urls),
    
    # ===== AUTENTICACIÓN MVT (HTML/Sesiones) =====
    # Mantiene el sistema existente intacto
    path('accounts/', include('accounts.urls')),
    
    # ===== API REST (JWT) =====
    # Nuevos endpoints para móviles/SPA
    path('api/', include('api.urls')),
    
    # ===== SISTEMA CONTABLE MVT =====
    # Apps del sistema contable con autenticación por sesiones
    path('empresas/', include('empresas.urls')),
    path('catalogos/', include('catalogos.urls')),
    path('facturacion/', include('facturacion.urls')),
    path('tesoreria/', include('tesoreria.urls')),
    path('contabilidad/', include('contabilidad.urls')),
    path('reportes/', include('reportes.urls')),
    
    # ===== PÁGINA PRINCIPAL =====
    # Redirige según el estado de autenticación
    path('', home_view, name='home'),
]
