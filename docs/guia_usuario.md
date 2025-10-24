# Guía de Usuario - S_CONTABLE

## Sistema Contable Colombiano

### Tabla de Contenidos
1. [Introducción](#introducción)
2. [Primeros Pasos](#primeros-pasos)
3. [Gestión de Empresas](#gestión-de-empresas)
4. [Catálogos](#catálogos)
5. [Facturación](#facturación)
6. [Tesorería](#tesorería)
7. [Contabilidad](#contabilidad)
8. [Reportes](#reportes)
9. [Solución de Problemas](#solución-de-problemas)

---

## Introducción

**S_CONTABLE** es un sistema contable integral diseñado específicamente para empresas colombianas. Permite gestionar múltiples empresas desde una sola cuenta de usuario, con roles diferenciados y cumplimiento de la normativa contable colombiana.

### Características Principales
- ✅ **Multi-empresa**: Gestiona varias empresas desde una cuenta
- ✅ **Roles de usuario**: Admin, Contador, Operador
- ✅ **Facturación electrónica**: Compatible con normativa DIAN
- ✅ **Contabilidad completa**: Plan de cuentas, asientos automáticos
- ✅ **Reportes contables**: Diario, Mayor, Balance, PyG
- ✅ **Tesorería integrada**: Cobros, pagos y flujo de caja

---

## Primeros Pasos

### 1. Iniciar Sesión

1. Accede a la URL del sistema: `http://localhost:8000`
2. Ingresa tu **usuario** y **contraseña**
3. Haz clic en **"Iniciar Sesión"**

![Login](screenshots/login.png)

### 2. Seleccionar Empresa

Si tienes acceso a múltiples empresas:

1. En el **Dashboard**, verás la empresa activa en la barra lateral
2. Para cambiar de empresa, haz clic en **"Cambiar Empresa"**
3. Selecciona la empresa con la que deseas trabajar

![Cambiar Empresa](screenshots/cambiar_empresa.png)

### 3. Navegación Principal

El sistema utiliza una **barra lateral** con los siguientes módulos:

- 🏠 **Dashboard**: Resumen ejecutivo
- 🏢 **Empresas**: Gestión de empresas (solo Admin)
- 👥 **Catálogos**: Terceros, productos, impuestos
- 🧾 **Facturación**: Crear y gestionar facturas
- 💰 **Tesorería**: Cobros, pagos y cuentas bancarias
- 📊 **Contabilidad**: Plan de cuentas y asientos
- 📈 **Reportes**: Informes contables

---

## Gestión de Empresas

### Crear Nueva Empresa

**Requisitos**: Rol de **Administrador**

1. Ve a **Empresas** → **Nueva Empresa**
2. Completa la información:
   - **NIT**: Formato 123456789-0
   - **Razón Social**: Nombre legal de la empresa
   - **Dirección**: Dirección completa
   - **Teléfono**: Número de contacto
   - **Email**: Correo corporativo

3. Haz clic en **"Guardar"**

![Nueva Empresa](screenshots/nueva_empresa.png)

### Gestionar Usuarios de Empresa

1. Ve a **Empresas** → Selecciona una empresa → **"Gestionar Perfiles"**
2. Haz clic en **"Agregar Usuario"**
3. Selecciona el **usuario** y asigna un **rol**:
   - **Admin**: Control total de la empresa
   - **Contador**: Puede confirmar documentos y ver todos los reportes
   - **Operador**: Solo puede crear borradores y ver reportes básicos

4. Haz clic en **"Asignar"**

---

## Catálogos

### Terceros (Clientes y Proveedores)

#### Crear Nuevo Tercero

1. Ve a **Catálogos** → **Terceros** → **"Nuevo Tercero"**
2. Completa la información:
   - **Tipo**: Cliente, Proveedor o Ambos
   - **Documento**: CC, NIT, etc.
   - **Número**: Sin puntos ni espacios
   - **Razón Social**: Nombre completo
   - **Datos de contacto**: Dirección, teléfono, email

3. Haz clic en **"Guardar"**

![Nuevo Tercero](screenshots/nuevo_tercero.png)

### Productos y Servicios

#### Crear Nuevo Producto

1. Ve a **Catálogos** → **Productos** → **"Nuevo Producto"**
2. Completa la información:
   - **Código**: Código interno único
   - **Nombre**: Descripción del producto
   - **Tipo**: Producto o Servicio
   - **Precio de Venta**: Valor sin impuestos
   - **Impuesto**: Selecciona el impuesto aplicable
   - **Inventariable**: Si maneja stock

3. Haz clic en **"Guardar"**

### Impuestos

#### Configurar Impuestos

1. Ve a **Catálogos** → **Impuestos** → **"Nuevo Impuesto"**
2. Configura:
   - **Código**: IVA19, ICA, etc.
   - **Nombre**: Descripción del impuesto
   - **Tipo**: IVA, ICA, Retención, etc.
   - **Porcentaje**: Valor del impuesto (ej: 19.00)

3. Haz clic en **"Guardar"**

---

## Facturación

### Crear Nueva Factura

1. Ve a **Facturación** → **"Nueva Factura"**
2. **Datos de la Factura**:
   - **Cliente**: Selecciona de la lista
   - **Fecha**: Fecha de emisión
   - **Tipo de Venta**: Contado o Crédito
   - **Método de Pago**: Solo para ventas de contado

3. **Agregar Productos**:
   - Haz clic en **"Agregar Línea"**
   - Selecciona el **producto**
   - Ingresa la **cantidad**
   - El sistema calculará automáticamente los totales

4. **Guardar como Borrador** o **Confirmar Factura**

![Nueva Factura](screenshots/nueva_factura.png)

### Confirmar Factura

**Requisitos**: Rol de **Contador** o **Administrador**

1. Ve a **Facturación** → Selecciona una factura en borrador
2. Verifica que todos los datos sean correctos
3. Haz clic en **"Confirmar Factura"**
4. El sistema generará automáticamente el **asiento contable**

### Ver Asiento Contable de la Factura

1. En el detalle de la factura confirmada
2. Haz clic en **"Ver Asiento Contable"**
3. Verás las partidas generadas automáticamente:
   - **Venta Contado**: Débito Caja, Crédito Ingresos, Crédito IVA
   - **Venta Crédito**: Débito Clientes, Crédito Ingresos, Crédito IVA

---

## Tesorería

### Registrar Cobro a Cliente

1. Ve a **Tesorería** → **Cobros** → **"Nuevo Cobro"**
2. Completa la información:
   - **Cliente**: Selecciona el cliente
   - **Factura**: Opcional, selecciona la factura que se está pagando
   - **Método de Pago**: Efectivo, transferencia, etc.
   - **Valor**: Monto del cobro
   - **Referencia**: Número de cheque, transferencia, etc.

3. Haz clic en **"Registrar Cobro"**
4. El sistema generará el asiento: Débito Caja, Crédito Clientes

![Nuevo Cobro](screenshots/nuevo_cobro.png)

### Gestionar Cuentas Bancarias

1. Ve a **Tesorería** → **Cuentas Bancarias** → **"Nueva Cuenta"**
2. Configura:
   - **Nombre**: Descripción de la cuenta
   - **Tipo**: Ahorros, Corriente, Caja
   - **Banco**: Nombre del banco
   - **Número de Cuenta**: Si aplica

3. Haz clic en **"Guardar"**

---

## Contabilidad

### Plan de Cuentas

#### Crear Plan de Cuentas Básico

**Requisitos**: Rol de **Contador** o **Administrador**

1. Ve a **Contabilidad** → **Plan de Cuentas**
2. Si no tienes cuentas, haz clic en **"Crear Plan Básico"**
3. El sistema creará automáticamente las cuentas principales:
   - **1**: ACTIVO
   - **1105**: CAJA
   - **1305**: CLIENTES
   - **2408**: IVA POR PAGAR
   - **4135**: INGRESOS POR VENTAS

#### Agregar Nueva Cuenta

1. Ve a **Contabilidad** → **Plan de Cuentas** → **"Nueva Cuenta"**
2. Configura:
   - **Código**: Código numérico único
   - **Nombre**: Descripción de la cuenta
   - **Naturaleza**: Débito o Crédito
   - **Tipo**: Activo, Pasivo, Patrimonio, Ingreso, Gasto
   - **Cuenta Padre**: Si es una subcuenta
   - **Acepta Movimiento**: Si puede tener partidas

### Asientos Contables Manuales

#### Crear Asiento Manual

**Requisitos**: Rol de **Contador** o **Administrador**

1. Ve a **Contabilidad** → **Asientos** → **"Nuevo Asiento"**
2. **Datos del Asiento**:
   - **Fecha**: Fecha del asiento
   - **Concepto**: Descripción del asiento

3. **Agregar Partidas**:
   - Haz clic en **"Agregar Partida"**
   - Selecciona la **cuenta**
   - Ingresa el **valor** en Débito o Crédito
   - Repite para todas las partidas

4. **Validar Cuadre**: El sistema verifica que Débitos = Créditos
5. **Confirmar Asiento**

![Nuevo Asiento](screenshots/nuevo_asiento.png)

### Regla Contable Fundamental

⚠️ **IMPORTANTE**: En todos los asientos debe cumplirse:
```
ΣDÉBITOS = ΣCRÉDITOS
```

El sistema no permitirá confirmar asientos que no estén cuadrados.

---

## Reportes

### Libro Diario

1. Ve a **Reportes** → **Libro Diario**
2. Selecciona el **rango de fechas**
3. Haz clic en **"Generar Reporte"**
4. El reporte muestra todos los asientos del período con sus partidas

### Libro Mayor

1. Ve a **Reportes** → **Libro Mayor**
2. Opciones:
   - **Todas las cuentas**: Reporte completo
   - **Cuenta específica**: Solo una cuenta
3. Selecciona el **rango de fechas**
4. Haz clic en **"Generar Reporte"**

### Balance de Comprobación

1. Ve a **Reportes** → **Balance de Comprobación**
2. Selecciona la **fecha de corte**
3. El reporte muestra todas las cuentas con:
   - Saldo inicial
   - Movimientos del período
   - Saldo final
   - Columnas de saldos deudor y acreedor

### Estado de Resultados (PyG)

**Requisitos**: Rol de **Contador** o **Administrador**

1. Ve a **Reportes** → **Estado de Resultados**
2. Selecciona el **período** (mes, trimestre, año)
3. El reporte muestra:
   - Ingresos operacionales
   - Costos y gastos
   - Utilidad del período

### Balance General

**Requisitos**: Rol de **Contador** o **Administrador**

1. Ve a **Reportes** → **Balance General**
2. Selecciona la **fecha de corte**
3. El reporte muestra:
   - Activos
   - Pasivos
   - Patrimonio
   - Verificación: Activo = Pasivo + Patrimonio

### Exportar Reportes

Todos los reportes pueden exportarse en:
- **HTML**: Para visualización en pantalla
- **CSV**: Para análisis en Excel
- **PDF**: Para impresión (si está configurado)

---

## Solución de Problemas

### Problemas Comunes

#### "No tienes acceso a ninguna empresa"

**Causa**: Tu usuario no tiene perfiles asignados a empresas.
**Solución**: Contacta al administrador para que te asigne a una empresa.

#### "Asiento no está cuadrado"

**Causa**: La suma de débitos no es igual a la suma de créditos.
**Solución**: 
1. Revisa todas las partidas del asiento
2. Verifica que los valores estén correctos
3. Asegúrate de que Σ Débitos = Σ Créditos

#### "La cuenta no acepta movimiento"

**Causa**: Intentas crear una partida en una cuenta de resumen.
**Solución**: Usa una cuenta de detalle (subcuenta) que sí acepte movimiento.

#### Error al confirmar factura

**Causa**: Faltan cuentas contables necesarias.
**Solución**:
1. Ve a **Contabilidad** → **Plan de Cuentas**
2. Crea o verifica que existan las cuentas:
   - 1105 (Caja)
   - 1305 (Clientes)
   - 4135 (Ingresos)
   - 2408 (IVA por pagar)

### Mensajes del Sistema

#### Mensajes de Éxito ✅
- **Verde**: Operación completada correctamente
- Aparecen en la parte superior de la pantalla
- Se ocultan automáticamente después de unos segundos

#### Mensajes de Error ❌
- **Rojo**: Error que impide completar la operación
- Revisa los datos ingresados y corrige los errores
- Si persiste, contacta al administrador

#### Mensajes de Advertencia ⚠️
- **Amarillo**: Situaciones que requieren atención
- No impiden la operación pero es recomendable revisarlas

### Cerrar Sesión

1. Haz clic en tu **nombre de usuario** (esquina superior derecha)
2. Selecciona **"Cerrar Sesión"**
3. Serás redirigido a la página de login

---

## Contacto y Soporte

Para soporte técnico o consultas sobre el sistema:

- **Email**: soporte@scontable.com
- **Teléfono**: +57 (1) 123-4567
- **Horario**: Lunes a Viernes, 8:00 AM - 6:00 PM

---

## Notas Importantes

1. **Respaldos**: El sistema realiza respaldos automáticos, pero es recomendable exportar reportes importantes regularmente.

2. **Permisos**: Respeta los roles asignados. Solo los contadores pueden confirmar documentos.

3. **Normativa**: El sistema está diseñado para cumplir con la normativa contable colombiana vigente.

4. **Actualizaciones**: Las actualizaciones del sistema se realizan automáticamente sin afectar los datos.

---

*Última actualización: Octubre 2024*
*Versión del sistema: 1.0.0*
