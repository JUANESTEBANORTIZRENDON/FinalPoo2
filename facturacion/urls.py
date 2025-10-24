from django.urls import path
from . import views

app_name = 'facturacion'

urlpatterns = [
    # Listado y gestión de facturas
    path('', views.FacturaListView.as_view(), name='factura_list'),
    path('crear/', views.FacturaCreateView.as_view(), name='factura_create'),
    path('<int:pk>/', views.FacturaDetailView.as_view(), name='factura_detail'),
    path('<int:pk>/editar/', views.FacturaUpdateView.as_view(), name='factura_update'),
    path('<int:pk>/eliminar/', views.FacturaDeleteView.as_view(), name='factura_delete'),
    
    # Acciones sobre facturas
    path('<int:pk>/confirmar/', views.confirmar_factura, name='confirmar'),
    path('<int:pk>/anular/', views.anular_factura, name='anular'),
    path('<int:pk>/duplicar/', views.duplicar_factura, name='duplicar'),
    
    # Gestión de detalles de factura
    path('<int:factura_pk>/detalles/', views.FacturaDetalleListView.as_view(), name='detalles_lista'),
    path('<int:factura_pk>/detalles/crear/', views.FacturaDetalleCreateView.as_view(), name='detalles_crear'),
    path('<int:factura_pk>/detalles/<int:pk>/editar/', views.FacturaDetalleUpdateView.as_view(), name='detalles_editar'),
    path('<int:factura_pk>/detalles/<int:pk>/eliminar/', views.FacturaDetalleDeleteView.as_view(), name='detalles_eliminar'),
    
    # Reportes y exportación
    path('<int:pk>/pdf/', views.factura_pdf, name='pdf'),
    path('<int:pk>/imprimir/', views.factura_imprimir, name='imprimir'),
    path('reporte/', views.FacturaReporteView.as_view(), name='reporte'),
    path('exportar/', views.exportar_facturas, name='exportar'),
    
    # AJAX endpoints
    path('api/siguiente-numero/', views.obtener_siguiente_numero, name='api_siguiente_numero'),
    path('api/calcular-totales/', views.calcular_totales_factura, name='api_calcular_totales'),
]
