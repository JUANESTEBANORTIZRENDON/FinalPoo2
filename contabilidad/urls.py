from django.urls import path
from . import views

app_name = 'contabilidad'

urlpatterns = [
    # Dashboard de contabilidad
    path('', views.ContabilidadIndexView.as_view(), name='index'),
    
    # Plan de cuentas
    path('plan-cuentas/', views.CuentaContableListView.as_view(), name='cuentas_lista'),
    path('plan-cuentas/crear/', views.CuentaContableCreateView.as_view(), name='cuentas_crear'),
    path('plan-cuentas/<int:pk>/', views.CuentaContableDetailView.as_view(), name='cuentas_detalle'),
    path('plan-cuentas/<int:pk>/editar/', views.CuentaContableUpdateView.as_view(), name='cuentas_editar'),
    path('plan-cuentas/<int:pk>/eliminar/', views.CuentaContableDeleteView.as_view(), name='cuentas_eliminar'),
    path('plan-cuentas/crear-basico/', views.crear_plan_cuentas_basico, name='crear_plan_basico'),
    
    # Asientos contables
    path('asientos/', views.AsientoListView.as_view(), name='asientos_lista'),
    path('asientos/crear/', views.AsientoCreateView.as_view(), name='asientos_crear'),
    path('asientos/<int:pk>/', views.AsientoDetailView.as_view(), name='asientos_detalle'),
    path('asientos/<int:pk>/editar/', views.AsientoUpdateView.as_view(), name='asientos_editar'),
    path('asientos/<int:pk>/eliminar/', views.AsientoDeleteView.as_view(), name='asientos_eliminar'),
    
    # Acciones sobre asientos
    path('asientos/<int:pk>/confirmar/', views.confirmar_asiento, name='asientos_confirmar'),
    path('asientos/<int:pk>/anular/', views.anular_asiento, name='asientos_anular'),
    path('asientos/<int:pk>/duplicar/', views.duplicar_asiento, name='asientos_duplicar'),
    path('asientos/<int:pk>/reversar/', views.reversar_asiento, name='asientos_reversar'),
    
    # Gestión de partidas
    path('asientos/<int:asiento_pk>/partidas/', views.PartidaListView.as_view(), name='partidas_lista'),
    path('asientos/<int:asiento_pk>/partidas/crear/', views.PartidaCreateView.as_view(), name='partidas_crear'),
    path('asientos/<int:asiento_pk>/partidas/<int:pk>/editar/', views.PartidaUpdateView.as_view(), name='partidas_editar'),
    path('asientos/<int:asiento_pk>/partidas/<int:pk>/eliminar/', views.PartidaDeleteView.as_view(), name='partidas_eliminar'),
    
    # Consultas contables
    path('consultas/saldos/', views.ConsultaSaldosView.as_view(), name='consulta_saldos'),
    path('consultas/movimientos/', views.ConsultaMovimientosView.as_view(), name='consulta_movimientos'),
    path('consultas/cuenta/<int:cuenta_pk>/', views.ConsultaCuentaView.as_view(), name='consulta_cuenta'),
    
    # AJAX endpoints
    path('api/siguiente-numero-asiento/', views.obtener_siguiente_numero_asiento, name='api_siguiente_numero_asiento'),
    path('api/cuentas/buscar/', views.buscar_cuentas, name='api_buscar_cuentas'),
    path('api/validar-cuadre/', views.validar_cuadre_asiento, name='api_validar_cuadre'),
    path('api/cuenta/<int:pk>/saldo/', views.obtener_saldo_cuenta, name='api_saldo_cuenta'),
]
