# 🏦 Módulo de Tesorería

**Funcionalidades implementadas**

- **Gestión de cuentas bancarias**: Creación, edición y desactivación de cuentas
- **Registro de cobros y pagos**: Con soporte para múltiples métodos de pago
- **Flujo de caja**: Visualización de ingresos, egresos y saldos acumulados
- **Saldos por cuenta**: Reporte de saldos actuales por cuenta bancaria
- **Reporte de pagos por período**: Filtrado por fechas, tipos de pago y estados
- **Exportación a CSV**: Para reportes de pagos y movimientos
- **Conciliación bancaria**: Modelo ExtractoBancario para conciliación
- **Envío de facturas por email**: Integración con servidor SMTP

## 1) Gestión de Cuentas Bancarias

- **Rutas principales**:
  - Listado: `/tesoreria/cuentas/`
  - Nueva cuenta: `/tesoreria/cuentas/nueva/`
  - Editar: `/tesoreria/cuentas/editar/<id>/`
  - Desactivar: `/tesoreria/cuentas/desactivar/<id>/`

## 2) Flujo de Caja

- **Ruta**: `/tesoreria/flujo-caja/`
- **Filtros**:
  - Rango de fechas
  - Cuenta bancaria específica
- **Métricas mostradas**:
  - Total ingresos
  - Total egresos
  - Flujo neto
  - Saldo acumulado por movimiento

## 3) Saldos por Cuenta

- **Ruta**: `/tesoreria/saldos-cuentas/`
- **Muestra**:
  - Saldo inicial
  - Total ingresos
  - Total egresos
  - Saldo actual
  - Saldo consolidado

## 4) Reporte de Pagos

- **Ruta**: `/tesoreria/pagos-periodo/`
- **Filtros**:
  - Rango de fechas
  - Tipo de pago (todos, cobro, egreso)
  - Estado (todos, pendiente, pagado, anulado)
- **Acciones**:
  - Exportar a CSV
  - Límite de 100 registros en la vista

## 5) Configuración de Correo

Para el envío de facturas por email, configurar en `.env`:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu_correo@dominio.com
EMAIL_HOST_PASSWORD=app_password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=Contabilidad <tu_correo@dominio.com>
```

## 6) Conciliación Bancaria

- **Modelo**: `ExtractoBancario`
- **Migración**: `0004_extractobancario.py`
- **Panel de administración**:
  - Registro de extractos bancarios
  - Conciliación manual con movimientos

## 7) Estructura de Archivos

````
tesoreria/
├── services/
│   ├── __init__.py
│   ├── emailing.py      # Lógica de envío de correos
│   └── reportes.py      # Generación de reportes
├── templates/tesoreria/
│   ├── flujo_caja.html
│   ├── saldos_cuentas.html
│   ├── pagos_periodo.html
│   └── emails/
│       └── factura_email.html
└── views/
    ├── __init__.py
    ├── pagos.py
    └── reportes.py

## Cómo probar
1. Aplicar migraciones:
   ```bash
   python manage.py migrate tesoreria
````

2. Navegar a las diferentes secciones:
   - Flujo de caja: `/tesoreria/flujo-caja/`
   - Saldos por cuenta: `/tesoreria/saldos-cuentas/`
   - Reporte de pagos: `/tesoreria/pagos-periodo/`
   - Envío de facturas: Hacer POST a `/tesoreria/facturas/<id>/enviar/`

## Próximas Mejoras

- [ ] Implementar conciliación automática
- [ ] Gráficos para visualización de datos
- [ ] Exportación a PDF para reportes
- [ ] Notificaciones para vencimientos

**Última actualización:** 09 Nov 2025 · **Responsable:** Sneyder
