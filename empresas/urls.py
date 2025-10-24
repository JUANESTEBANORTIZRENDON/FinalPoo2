from django.urls import path
from . import views

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
]
