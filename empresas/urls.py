from django.urls import path
from . import views
from . import views_admin
from . import views_dev_auth

app_name = 'empresas'

urlpatterns = [
    # Listado y gestión de empresas
    path('', views.EmpresaListView.as_view(), name='empresa_list'),
    path('crear/', views.EmpresaCreateView.as_view(), name='empresa_create'),
    path('<int:pk>/', views.EmpresaDetailView.as_view(), name='empresa_detail'),
    path('<int:pk>/editar/', views.EmpresaUpdateView.as_view(), name='empresa_update'),
    
    # Gestión de perfiles de usuario en empresas
    path('<int:empresa_pk>/perfiles/', views.PerfilEmpresaListView.as_view(), name='perfil_list'),
    path('<int:empresa_pk>/perfiles/crear/', views.PerfilEmpresaCreateView.as_view(), name='perfil_create'),
    path('<int:empresa_pk>/perfiles/<int:pk>/editar/', views.PerfilEmpresaUpdateView.as_view(), name='perfil_update'),
    path('<int:empresa_pk>/perfiles/<int:pk>/eliminar/', views.PerfilEmpresaDeleteView.as_view(), name='perfil_delete'),
    
    # Cambio de empresa activa
    path('cambiar-empresa/', views.CambiarEmpresaView.as_view(), name='cambiar_empresa'),
    path('seleccionar/', views.seleccionar_empresa, name='seleccionar_empresa'),
    
    # Dashboards por rol
    path('contador/dashboard/', views.contador_dashboard, name='contador_dashboard'),
    path('operador/dashboard/', views.operador_dashboard, name='operador_dashboard'),
    path('observador/dashboard/', views.observador_dashboard, name='observador_dashboard'),
    
    # URLs del módulo administrador
    path('admin/dashboard/', views_admin.dashboard_admin, name='admin_dashboard'),
    
    # Dashboards por rol
    path('contador/dashboard/', views_admin.dashboard_contador, name='contador_dashboard'),
    path('operador/dashboard/', views_admin.dashboard_operador, name='operador_dashboard'),
    path('observador/dashboard/', views_admin.dashboard_observador, name='observador_dashboard'),
    
    path('admin/empresas/', views_admin.gestionar_empresas, name='admin_gestionar_empresas'),
    path('admin/empresas/crear/', views_admin.crear_empresa, name='admin_crear_empresa'),
    path('admin/empresas/<int:empresa_id>/', views_admin.ver_empresa, name='admin_ver_empresa'),
    path('admin/empresas/<int:empresa_id>/editar/', views_admin.editar_empresa, name='admin_editar_empresa'),
    path('admin/empresas/<int:empresa_id>/eliminar/', views_admin.eliminar_empresa, name='admin_eliminar_empresa'),
    path('admin/usuarios/', views_admin.gestionar_usuarios, name='admin_gestionar_usuarios'),
    path('admin/usuarios/crear/', views_admin.crear_usuario, name='admin_crear_usuario'),
    path('admin/usuarios/<int:usuario_id>/', views_admin.ver_usuario, name='admin_ver_usuario'),
    path('admin/usuarios/<int:usuario_id>/editar/', views_admin.editar_usuario, name='admin_editar_usuario'),
    path('admin/usuarios/<int:usuario_id>/asignar/', views_admin.asignar_usuario_empresa, name='admin_asignar_usuario'),
    path('admin/desactivar-asignacion/<int:perfil_id>/', views_admin.desactivar_asignacion, name='admin_desactivar_asignacion'),
    path('admin/gestion-contadores/', views_admin.gestion_contadores_auxiliares, name='admin_gestion_contadores'),
    path('admin/historial/', views_admin.historial_cambios, name='admin_historial_cambios'),
    path('admin/historial/<int:cambio_id>/', views_admin.detalle_historial_cambio, name='admin_detalle_historial_cambio'),
    path('admin/historial/exportar/', views_admin.exportar_historial, name='admin_exportar_historial'),
    path('admin/ajax/empresa/<int:empresa_id>/', views_admin.ajax_empresa_info, name='admin_ajax_empresa_info'),
    
    # Verificación de desarrollador
    path('dev-auth/', views_dev_auth.dev_auth_required, name='dev_auth_required'),
]
