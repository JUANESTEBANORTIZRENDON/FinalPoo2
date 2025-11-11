from django.urls import path
from . import views

app_name = 'catalogos'

urlpatterns = [
    # Dashboard de catálogos
    path('', views.CatalogosIndexView.as_view(), name='index'),
    
    # Terceros (clientes y proveedores)
    path('terceros/', views.TerceroListView.as_view(), name='tercero_list'),
    path('terceros/crear/', views.TerceroCreateView.as_view(), name='tercero_create'),
    path('terceros/<int:pk>/', views.TerceroDetailView.as_view(), name='tercero_detail'),
    path('terceros/<int:pk>/editar/', views.TerceroUpdateView.as_view(), name='tercero_update'),
    path('terceros/<int:pk>/eliminar/', views.TerceroDeleteView.as_view(), name='tercero_delete'),
    
    # Impuestos
    path('impuestos/', views.ImpuestoListView.as_view(), name='impuestos_lista'),
    path('impuestos/crear/', views.ImpuestoCreateView.as_view(), name='impuestos_crear'),
    path('impuestos/<int:pk>/', views.ImpuestoDetailView.as_view(), name='impuestos_detalle'),
    path('impuestos/<int:pk>/editar/', views.ImpuestoUpdateView.as_view(), name='impuestos_editar'),
    path('impuestos/<int:pk>/eliminar/', views.ImpuestoDeleteView.as_view(), name='impuestos_eliminar'),
    
    # Métodos de pago
    path('metodos-pago/', views.MetodoPagoListView.as_view(), name='metodos_pago_lista'),
    path('metodos-pago/crear/', views.MetodoPagoCreateView.as_view(), name='metodos_pago_crear'),
    path('metodos-pago/<int:pk>/', views.MetodoPagoDetailView.as_view(), name='metodos_pago_detalle'),
    path('metodos-pago/<int:pk>/editar/', views.MetodoPagoUpdateView.as_view(), name='metodos_pago_editar'),
    path('metodos-pago/<int:pk>/eliminar/', views.MetodoPagoDeleteView.as_view(), name='metodos_pago_eliminar'),
    
    # Productos
    path('productos/', views.ProductoListView.as_view(), name='producto_list'),
    path('productos/crear/', views.ProductoCreateView.as_view(), name='producto_create'),
    path('productos/<int:pk>/', views.ProductoDetailView.as_view(), name='producto_detail'),
    path('productos/<int:pk>/editar/', views.ProductoUpdateView.as_view(), name='producto_update'),
    # path('productos/<int:pk>/toggle-activo/', views.producto_toggle_activo, name='producto_toggle_activo'),
    
    # AJAX endpoints para búsquedas
    path('api/terceros/buscar/', views.buscar_terceros, name='api_buscar_terceros'),
    path('api/productos/buscar/', views.buscar_productos, name='api_buscar_productos'),
    path('api/productos/<int:pk>/info/', views.info_producto, name='api_info_producto'),
]
