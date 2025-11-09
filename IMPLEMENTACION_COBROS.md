# Implementación de Gestión de Cobros

## 📋 Resumen
Se ha implementado un sistema completo de gestión de cobros con las siguientes funcionalidades:

### ✅ Funcionalidades Implementadas

#### 1. **Editar Cobro**
- Permite modificar cobros que estén en estado "borrador"
- Formulario completo con validaciones
- Ruta: `/tesoreria/cobros/<id>/editar/`
- Template: `cobros_editar.html`

#### 2. **Eliminar Cobro**
- Permite eliminar cobros en estado "borrador"
- Confirmación antes de eliminar
- Muestra información completa del cobro antes de eliminarlo
- Ruta: `/tesoreria/cobros/<id>/eliminar/`
- Template: `cobros_eliminar.html`

#### 3. **Activar Cobro**
- Cambia el estado del cobro de "borrador" a "confirmado"
- **Genera automáticamente una factura** asociada al cobro
- La factura se crea con:
  - Número automático (FAC-000001, FAC-000002, etc.)
  - Estado "confirmada"
  - Mismo cliente, fecha y valor del cobro
  - Tipo de venta: "contado"
- Ruta: `/tesoreria/cobros/<id>/activar/` (POST)
- Confirmación mediante JavaScript

#### 4. **Generar PDF de Factura**
- Genera un PDF profesional de la factura
- **Nombre del archivo**: `CODIGO_NOMBRECLIENTE.pdf` (ej: `FAC-000001_Juan_Perez.pdf`)
- Incluye:
  - Información de la empresa
  - Datos de la factura
  - Información del cliente
  - Totales (subtotal, impuestos, total)
  - Observaciones
- Ruta: `/tesoreria/facturas/<factura_id>/pdf/`
- Descarga directa del PDF

### 🎨 Interfaz de Usuario

#### Lista de Cobros (`cobros_lista.html`)
Ahora incluye botones de acción según el estado del cobro:

**Para cobros en estado "borrador":**
- 👁️ **Ver**: Ver detalles del cobro
- ✏️ **Editar**: Modificar el cobro
- ✅ **Activar**: Activar cobro y generar factura (con confirmación)
- 🗑️ **Eliminar**: Eliminar el cobro

**Para cobros en estado "confirmado":**
- 👁️ **Ver**: Ver detalles del cobro
- 📄 **Ver PDF**: Descargar la factura en PDF

### 📦 Dependencias Agregadas
Se agregaron las siguientes librerías en `requirements.txt`:
```
reportlab==4.0.7
weasyprint==60.1
```

### 🔧 Archivos Modificados/Creados

#### Archivos Modificados:
1. `tesoreria/views.py` - Nuevas vistas y función de generación de PDF
2. `tesoreria/urls.py` - Nuevas rutas
3. `templates/tesoreria/cobros_lista.html` - Botones de acción actualizados
4. `requirements.txt` - Dependencias para PDF

#### Archivos Creados:
1. `templates/tesoreria/cobros_editar.html` - Formulario de edición
2. `templates/tesoreria/cobros_eliminar.html` - Confirmación de eliminación
3. `IMPLEMENTACION_COBROS.md` - Este documento

### 🚀 Cómo Usar

#### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

#### 2. Flujo de Trabajo
1. **Crear un cobro**: Estado inicial "borrador"
2. **Editar si es necesario**: Mientras esté en borrador
3. **Activar el cobro**: Genera automáticamente la factura
4. **Descargar PDF**: Desde el botón "Ver PDF" en la lista

### 🔐 Seguridad
- Solo se pueden editar/eliminar cobros en estado "borrador"
- Validación de permisos por empresa (multi-tenant)
- Confirmación antes de activar o eliminar
- Token CSRF en todas las operaciones POST

### 📊 Modelo de Datos
El cobro (`Pago`) tiene relación con la factura (`Factura`):
- Campo: `factura` (ForeignKey opcional)
- Se establece automáticamente al activar el cobro

### 🎯 Próximos Pasos Sugeridos
1. Agregar detalles de productos/servicios a las facturas
2. Implementar envío de factura por email
3. Agregar reportes de cobros por período
4. Implementar conciliación bancaria

### 📝 Notas Técnicas
- El PDF se genera usando ReportLab con diseño profesional
- Colores y estilos personalizados para mejor presentación
- El nombre del archivo incluye el código de factura y nombre del cliente
- La función de activación es transaccional (crea factura y actualiza cobro)

---
**Desarrollado para**: Sistema Contable S_CONTABLE  
**Módulo**: Tesorería - Gestión de Cobros  
**Fecha**: Noviembre 2025
