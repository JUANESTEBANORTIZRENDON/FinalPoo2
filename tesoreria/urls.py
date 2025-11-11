from django.urls import path
from . import views

app_name = 'tesoreria'

urlpatterns = [
    # Dashboard de tesorería
    path('', views.TesoreriaIndexView.as_view(), name='index'),
    
    # Gestión de pagos
    path('pagos/', views.PagoListView.as_view(), name='pagos_lista'),
    path('pagos/crear/', views.PagoCreateView.as_view(), name='pagos_crear'),
    path('pagos/<int:pk>/', views.PagoDetailView.as_view(), name='pagos_detalle'),
    path('pagos/<int:pk>/editar/', views.PagoUpdateView.as_view(), name='pagos_editar'),
    path('pagos/<int:pk>/eliminar/', views.PagoDeleteView.as_view(), name='pagos_eliminar'),
    
    # Acciones sobre pagos
    path('pagos/<int:pk>/confirmar/', views.confirmar_pago, name='pagos_confirmar'),
    path('pagos/<int:pk>/anular/', views.anular_pago, name='pagos_anular'),
    
    # Cobros específicos
    path('cobros/', views.CobroListView.as_view(), name='cobros_lista'),
    path('cobros/crear/', views.CobroCreateView.as_view(), name='cobros_crear'),
    path('cobros/<int:pk>/editar/', views.CobroUpdateView.as_view(), name='cobros_editar'),
    path('cobros/<int:pk>/eliminar/', views.eliminar_cobro, name='cobros_eliminar'),
    path('cobros/<int:pk>/activar/', views.activar_cobro, name='cobros_activar'),
    path('cobros/<int:pk>/marcar-pagado/', views.marcar_cobro_pagado, name='cobros_marcar_pagado'),
    path('cobros/factura/<int:factura_pk>/', views.cobrar_factura, name='cobrar_factura'),
    
    # Generar PDF de factura
    path('facturas/<int:factura_pk>/pdf/', views.generar_factura_pdf, name='factura_pdf'),
    
    # Egresos específicos
    path('egresos/', views.EgresoListView.as_view(), name='egresos_lista'),
    path('egresos/crear/', views.EgresoCreateView.as_view(), name='egresos_crear'),
    path('egresos/<int:pk>/editar/', views.EgresoUpdateView.as_view(), name='egresos_editar'),
    path('egresos/<int:pk>/eliminar/', views.EgresoDeleteView.as_view(), name='egresos_eliminar'),
    
    # Gestión de cuentas bancarias
    path('cuentas-bancarias/', views.CuentaBancariaListView.as_view(), name='cuentas_lista'),
    path('cuentas-bancarias/crear/', views.CuentaBancariaCreateView.as_view(), name='cuentas_crear'),
    path('cuentas-bancarias/<int:pk>/', views.CuentaBancariaDetailView.as_view(), name='cuentas_detalle'),
    path('cuentas-bancarias/<int:pk>/editar/', views.CuentaBancariaUpdateView.as_view(), name='cuentas_editar'),
    path('cuentas-bancarias/<int:pk>/eliminar/', views.CuentaBancariaDeleteView.as_view(), name='cuentas_eliminar'),
    
    # Reportes de tesorería
    path('reportes/flujo-caja/', views.FlujoCajaView.as_view(), name='flujo_caja'),
    path('reportes/saldos-cuentas/', views.SaldosCuentasView.as_view(), name='saldos_cuentas'),
    path('reportes/pagos-periodo/', views.PagosPeriodoView.as_view(), name='pagos_periodo'),
    
    # AJAX endpoints
    path('api/siguiente-numero-pago/', views.obtener_siguiente_numero_pago, name='api_siguiente_numero_pago'),
    path('api/facturas-pendientes/<int:tercero_pk>/', views.facturas_pendientes_tercero, name='api_facturas_pendientes'),
    path('api/crear-cliente/', views.crear_cliente_ajax, name='crear_cliente_ajax'),
]
