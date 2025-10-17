"""
URLs para API REST con JWT
Endpoints para móviles/SPA que conviven con vistas MVT
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'api'

urlpatterns = [
    # ===== AUTENTICACIÓN JWT =====
    # POST /api/token/ - Obtener access + refresh tokens
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # POST /api/token/refresh/ - Renovar access token con refresh token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # GET /api/me/ - Información del usuario autenticado (requiere JWT)
    path('me/', views.me_view, name='me'),
    
    # POST /api/logout/ - Invalidar refresh token (blacklist)
    path('logout/', views.logout_view, name='logout'),
    
    # ===== REGISTRO Y ACTIVACIÓN =====
    # POST /api/registro/ - Crear usuario básico y enviar email de activación
    path('registro/', views.registro_view, name='registro'),
    
    # POST /api/registro-completo/ - Crear usuario con información completa
    path('registro-completo/', views.registro_completo_view, name='registro_completo'),
    
    # POST /api/activar/ - Activar cuenta con token del email
    path('activar/', views.activar_cuenta_view, name='activar'),
    
    # ===== RECUPERACIÓN DE CONTRASEÑA =====
    # POST /api/password/reset/ - Solicitar reset por email
    path('password/reset/', views.password_reset_view, name='password_reset'),
    
    # POST /api/password/reset/confirm/ - Confirmar reset con token
    path('password/reset/confirm/', views.password_reset_confirm_view, name='password_reset_confirm'),
]
