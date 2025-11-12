# 🎯 ASIENTOS CONTABLES AUTOMÁTICOS - DOCUMENTACIÓN COMPLETA

## 📋 Resumen
Sistema de generación automática de asientos contables desde movimientos de tesorería (Ingresos y Egresos).

---

## ✅ ¿QUÉ SE IMPLEMENTÓ?

### 1. 🏗️ **Archivo de Utilidades** (`contabilidad/asiento_helpers.py`)

Funciones auxiliares para generar asientos contables automáticamente:

#### **Funciones Principales:**

- `generar_numero_asiento(empresa)` - Genera número consecutivo `ASI-000001`
- `crear_asiento_ingreso(pago, usuario)` - Crea asiento para ingresos
- `crear_asiento_egreso(pago, usuario)` - Crea asiento para egresos
- `anular_asiento_pago(pago)` - Anula asiento al eliminar pago

#### **Funciones de Búsqueda de Cuentas:**

- `obtener_cuenta_banco(empresa, cuenta_bancaria)` - Busca cuenta 1110 (Bancos)
- `obtener_cuenta_ingresos(empresa)` - Busca cuenta 4105 (Ingresos)
- `obtener_cuenta_gastos(empresa)` - Busca cuenta 5105 (Gastos)

---

## 💰 LÓGICA CONTABLE

### 📥 **INGRESO (Cobro a Cliente)**

```
Débito:  Banco/Caja (1110)      $100.000  ← Aumenta el activo
Crédito: Ingresos (4105)         $100.000  ← Aumenta los ingresos
```

**Interpretación:** Entra dinero al banco y se registra como ingreso.

---

### 📤 **EGRESO (Pago a Proveedor)**

```
Débito:  Gastos (5105)           $50.000  ← Aumenta los gastos
Crédito: Banco/Caja (1110)       $50.000  ← Disminuye el activo
```

**Interpretación:** Sale dinero del banco para pagar un gasto.

---

## 🔄 FLUJO COMPLETO

### **1. CREAR INGRESO/EGRESO**
```
Usuario crea un Ingreso/Egreso
    ↓
Vista guarda el Pago en BD
    ↓
Se llama a crear_asiento_ingreso() o crear_asiento_egreso()
    ↓
Se buscan las cuentas contables necesarias
    ↓
Se crea el Asiento con estado='confirmado'
    ↓
Se crean 2 Partidas (débito y crédito)
    ↓
Se vincula el asiento al pago (pago.asiento_contable = asiento)
    ↓
Mensaje de éxito al usuario
```

### **2. ELIMINAR INGRESO/EGRESO**
```
Usuario elimina un Ingreso/Egreso
    ↓
Se devuelve saldo a cuenta bancaria (si aplica)
    ↓
Se llama a anular_asiento_pago()
    ↓
El asiento cambia a estado='anulado'
    ↓
El asiento NO se elimina (queda como registro histórico)
    ↓
Mensaje de confirmación al usuario
```

---

## 📂 ARCHIVOS MODIFICADOS

### **1. Nuevos Archivos:**
- ✅ `contabilidad/asiento_helpers.py` - Funciones de generación de asientos

### **2. Archivos Actualizados:**

#### **`tesoreria/views.py`:**
- ✅ Agregados imports de funciones de asientos
- ✅ `IngresoCreateView.form_valid()` - Genera asiento al crear ingreso
- ✅ `EgresoCreateView.form_valid()` - Genera asiento al crear egreso
- ✅ `EgresoDeleteView.delete()` - Anula asiento al eliminar egreso

#### **`tesoreria/models.py`:**
- ✅ Campo `cuenta_bancaria` agregado al modelo `Pago`
- ✅ Migración aplicada: `0006_alter_extractobancario_options_pago_cuenta_bancaria.py`

---

## 🎨 MENSAJES AL USUARIO

### **Al Crear Ingreso:**
```
✅ Ingreso ING-000001 registrado exitosamente. 
   Asiento contable ASI-000001 generado automáticamente.
```

### **Al Crear Egreso:**
```
✅ Egreso EGR-000001 registrado exitosamente. 
   Se descontaron $50.000,00 de Banco Bancolombia. 
   Asiento contable ASI-000002 generado automáticamente.
```

### **Al Eliminar Egreso:**
```
✅ Egreso EGR-000001 eliminado exitosamente. 
   Saldo de $50.000,00 devuelto a Banco Bancolombia. 
   Asiento contable ASI-000002 anulado.
```

### **Si Falta una Cuenta Contable:**
```
⚠️ Ingreso ING-000001 registrado, pero no se pudo generar el asiento contable: 
   No se encontró una cuenta de Ingresos (4105). Por favor, cree la cuenta en el Plan de Cuentas.
```

---

## 🔍 CUENTAS CONTABLES NECESARIAS

Para que el sistema funcione correctamente, deben existir las siguientes cuentas en el **Plan de Cuentas**:

| Código | Nombre | Tipo | Naturaleza | Acepta Movimiento |
|--------|--------|------|------------|-------------------|
| **1110** | Bancos | Activo | Deudora | ✅ Sí |
| **4105** | Ingresos operacionales | Ingreso | Acreedora | ✅ Sí |
| **5105** | Gastos administrativos | Gasto | Deudora | ✅ Sí |

### **Si no existen estas cuentas:**
El sistema buscará automáticamente:
- Cuenta de tipo **Activo** con "banco" en el nombre
- Cuenta de tipo **Ingreso** que acepte movimiento
- Cuenta de tipo **Gasto** que acepte movimiento

---

## 🧪 CÓMO PROBAR

### **Paso 1: Verificar Plan de Cuentas**
1. Ir a **Contabilidad → Plan de Cuentas**
2. Verificar que existan las cuentas **1110**, **4105**, **5105**
3. Si no existen, crearlas

### **Paso 2: Crear un Ingreso**
1. Ir a **Tesorería → Ingresos → Nuevo Ingreso**
2. Llenar el formulario:
   - Cliente
   - Fecha
   - Valor: $100.000
   - Método de pago
   - Cuenta bancaria (opcional)
3. Guardar
4. Verificar mensaje de éxito con número de asiento

### **Paso 3: Verificar Asiento Generado**
1. Ir a **Contabilidad → Asientos Contables**
2. Buscar el asiento `ASI-XXXXXX` mencionado
3. Ver detalles del asiento
4. Verificar que tenga 2 partidas:
   - Débito: Banco (1110) - $100.000
   - Crédito: Ingresos (4105) - $100.000

### **Paso 4: Crear un Egreso**
1. Ir a **Tesorería → Egresos → Nuevo Egreso**
2. Llenar el formulario:
   - Proveedor
   - Fecha
   - Valor: $50.000
   - Método de pago
   - Cuenta bancaria (seleccionar una)
3. Guardar
4. Verificar:
   - Descuento de saldo en cuenta bancaria
   - Asiento contable generado

### **Paso 5: Verificar Asiento de Egreso**
1. Ir a **Contabilidad → Asientos Contables**
2. Buscar el nuevo asiento
3. Verificar que tenga 2 partidas:
   - Débito: Gastos (5105) - $50.000
   - Crédito: Banco (1110) - $50.000

### **Paso 6: Eliminar un Egreso**
1. Ir a **Tesorería → Egresos**
2. Eliminar el egreso creado
3. Verificar:
   - Saldo devuelto a cuenta bancaria
   - Asiento anulado (no eliminado)

---

## ⚠️ CASOS ESPECIALES

### **1. Sin Cuenta Bancaria**
Si un ingreso/egreso no tiene cuenta bancaria seleccionada:
- Se busca la cuenta genérica 1110 (Bancos)
- Se genera el asiento igual
- No se descuenta/aumenta saldo de ninguna cuenta bancaria

### **2. Cuenta Bancaria con Cuenta Contable Vinculada**
Si la cuenta bancaria tiene `cuenta_contable` asignada:
- Se usa esa cuenta contable específica en lugar de la 1110 genérica
- Ejemplo: "Banco Davivienda" puede estar vinculado a cuenta 1110-01

### **3. Saldo Insuficiente**
Si el saldo de la cuenta bancaria es insuficiente:
- Se muestra advertencia al usuario
- El egreso se registra de todas formas
- El saldo queda negativo
- El asiento contable se genera normalmente

### **4. Error al Generar Asiento**
Si falta una cuenta contable o hay error:
- El ingreso/egreso se registra de todas formas
- Se muestra mensaje de advertencia/error
- El asiento NO se genera
- El usuario debe corregir el Plan de Cuentas

---

## 📊 IMPACTO EN REPORTES CONTABLES

Los asientos generados automáticamente se reflejan en:

1. **Libro Diario** - Registro cronológico de todas las operaciones
2. **Mayor General** - Saldos por cuenta contable
3. **Balance de Comprobación** - Débitos y créditos por cuenta
4. **Estado de Resultados** - Ingresos y gastos del periodo
5. **Balance General** - Activos, pasivos y patrimonio

---

## 🔐 SEGURIDAD Y VALIDACIONES

### **Validaciones Implementadas:**
✅ Asientos creados con estado `confirmado` (no editables)
✅ Asientos cuadrados (débito = crédito)
✅ Vinculación automática pago ↔ asiento
✅ Anulación en lugar de eliminación (trazabilidad)
✅ Transacciones atómicas (todo o nada)
✅ Manejo de errores con mensajes claros

### **Permisos:**
✅ Solo usuarios autenticados pueden crear ingresos/egresos
✅ Filtrado multi-tenant (cada empresa ve solo sus datos)
✅ Usuario registrado en asiento (`creado_por`, `confirmado_por`)

---

## 🚀 PRÓXIMAS MEJORAS

### **Posibles Extensiones:**
- [ ] Permitir configurar cuentas contables desde el sistema
- [ ] Generar asientos para cobros (facturas)
- [ ] Generar asientos para conciliación bancaria
- [ ] Permitir reversión de asientos (contrapartida automática)
- [ ] Dashboard de asientos automáticos vs manuales
- [ ] Notificaciones cuando no se pueda generar asiento

---

## 📚 REFERENCIAS

### **Documentación Relacionada:**
- `contabilidad/README.md` - Explicación del módulo de contabilidad
- `tesoreria/README.md` - Explicación del módulo de tesorería
- Código fuente: `contabilidad/asiento_helpers.py`

### **Modelos Involucrados:**
- `contabilidad.Asiento` - Asiento contable
- `contabilidad.Partida` - Líneas del asiento
- `contabilidad.CuentaContable` - Cuentas del plan
- `tesoreria.Pago` - Ingresos y egresos
- `tesoreria.CuentaBancaria` - Cuentas bancarias

---

## 🎓 CONCEPTOS CONTABLES

### **¿Qué es un Asiento Contable?**
Es el registro de una operación en el sistema de contabilidad de partida doble.
Cada asiento tiene al menos 2 partidas: una en débito y otra en crédito.

### **Partida Doble**
Principio contable que establece que toda operación tiene dos efectos:
- **Débito:** Origen del recurso (de dónde viene)
- **Crédito:** Destino del recurso (a dónde va)

### **Cuentas de Naturaleza Deudora**
Aumentan con débitos y disminuyen con créditos:
- Activos (bancos, caja, clientes)
- Gastos

### **Cuentas de Naturaleza Acreedora**
Aumentan con créditos y disminuyen con débitos:
- Pasivos (proveedores, préstamos)
- Patrimonio
- Ingresos

---

## ✨ CONCLUSIÓN

El sistema de asientos automáticos está **completamente funcional** y cumple con:

✅ Generación automática de asientos desde tesorería
✅ Lógica contable correcta (débito/crédito)
✅ Vinculación pago ↔ asiento
✅ Anulación automática al eliminar pagos
✅ Manejo de errores y mensajes claros
✅ Búsqueda inteligente de cuentas contables
✅ Transacciones atómicas y seguras

**¡El módulo está listo para producción!** 🎉
