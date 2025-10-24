from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    # Dashboard de reportes
    path('', views.ReportesIndexView.as_view(), name='index'),
    
    # Libro Diario
    path('diario/', views.LibroDiarioView.as_view(), name='diario'),
    path('diario/generar/', views.generar_libro_diario, name='diario_generar'),
    path('diario/exportar/', views.exportar_libro_diario, name='diario_exportar'),
    
    # Libro Mayor
    path('mayor/', views.LibroMayorView.as_view(), name='mayor'),
    path('mayor/generar/', views.generar_libro_mayor, name='mayor_generar'),
    path('mayor/exportar/', views.exportar_libro_mayor, name='mayor_exportar'),
    path('mayor/cuenta/<int:cuenta_pk>/', views.LibroMayorCuentaView.as_view(), name='mayor_cuenta'),
    
    # Balance de Comprobación
    path('balance-comprobacion/', views.BalanceComprobacionView.as_view(), name='balance_comprobacion'),
    path('balance-comprobacion/generar/', views.generar_balance_comprobacion, name='balance_comprobacion_generar'),
    path('balance-comprobacion/exportar/', views.exportar_balance_comprobacion, name='balance_comprobacion_exportar'),
    
    # Estado de Resultados (PyG)
    path('estado-resultados/', views.EstadoResultadosView.as_view(), name='estado_resultados'),
    path('estado-resultados/generar/', views.generar_estado_resultados, name='estado_resultados_generar'),
    path('estado-resultados/exportar/', views.exportar_estado_resultados, name='estado_resultados_exportar'),
    
    # Balance General
    path('balance-general/', views.BalanceGeneralView.as_view(), name='balance_general'),
    path('balance-general/generar/', views.generar_balance_general, name='balance_general_generar'),
    path('balance-general/exportar/', views.exportar_balance_general, name='balance_general_exportar'),
    
    # Flujo de Efectivo
    path('flujo-efectivo/', views.FlujoEfectivoView.as_view(), name='flujo_efectivo'),
    path('flujo-efectivo/generar/', views.generar_flujo_efectivo, name='flujo_efectivo_generar'),
    path('flujo-efectivo/exportar/', views.exportar_flujo_efectivo, name='flujo_efectivo_exportar'),
    
    # Gestión de configuraciones de reportes
    path('configuraciones/', views.ConfiguracionReporteListView.as_view(), name='configuraciones_lista'),
    path('configuraciones/crear/', views.ConfiguracionReporteCreateView.as_view(), name='configuraciones_crear'),
    path('configuraciones/<int:pk>/', views.ConfiguracionReporteDetailView.as_view(), name='configuraciones_detalle'),
    path('configuraciones/<int:pk>/editar/', views.ConfiguracionReporteUpdateView.as_view(), name='configuraciones_editar'),
    path('configuraciones/<int:pk>/eliminar/', views.ConfiguracionReporteDeleteView.as_view(), name='configuraciones_eliminar'),
    path('configuraciones/<int:pk>/usar/', views.usar_configuracion, name='configuraciones_usar'),
    
    # Historial de reportes generados
    path('historial/', views.ReporteGeneradoListView.as_view(), name='historial'),
    path('historial/<int:pk>/', views.ReporteGeneradoDetailView.as_view(), name='historial_detalle'),
    path('historial/<int:pk>/descargar/', views.descargar_reporte, name='historial_descargar'),
    
    # AJAX endpoints
    path('api/validar-periodo/', views.validar_periodo_reporte, name='api_validar_periodo'),
    path('api/preview/', views.preview_reporte, name='api_preview'),
]
