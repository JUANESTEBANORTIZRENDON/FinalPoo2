# 📋 DIVISIÓN DE TRABAJO - SISTEMA CONTABLE S_CONTABLE
**Fecha:** 5 de Noviembre de 2025  
**Proyecto:** Sistema Contable Multiempresa con Django  
**Equipo:** 4 desarrolladores (Gabo, Wiki, Sneyder, Estiven)

---

## 🎯 RESUMEN EJECUTIVO DEL PROYECTO

### Estado Actual (Lo que llevamos completado)

#### ✅ **COMPLETADO AL 100%**
1. **Infraestructura Base:**
   - Proyecto Django 5.2.7 configurado y funcionando
   - Base de datos PostgreSQL (Neon) conectada
   - Sistema de autenticación con sesiones (MVT)
   - API REST con JWT configurada (DRF + SimpleJWT)
   - GitHub Actions + SonarCloud (análisis de calidad)
   - Sistema de migraciones aplicadas correctamente

2. **Módulo de Empresas (Holding):**
   - ✅ Modelo `Empresa` completo
   - ✅ Modelo `PerfilEmpresa` (usuarios-empresas-roles)
   - ✅ Dashboard de administrador holding COMPLETO
   - ✅ CRUD completo de empresas
   - ✅ CRUD completo de usuarios
   - ✅ Sistema de asignación usuarios-empresas-roles
   - ✅ Historial de cambios con middleware
   - ✅ Exportación de historial a CSV
   - ✅ Estadísticas del holding
   - ✅ Sistema de cambio de empresa activa
   - ✅ Templates completos y funcionales

3. **Módulo de Autenticación (Accounts):**
   - ✅ Registro de usuarios completo (colombiano)
   - ✅ Login/Logout funcional
   - ✅ Recuperación de contraseña por email
   - ✅ Perfil de usuario extendido (PerfilUsuario)
   - ✅ Dashboard básico post-login
   - ✅ Sistema de activación de cuenta
   - ✅ API REST para registro y autenticación JWT

4. **Módulo de Catálogos:**
   - ✅ Modelo `Tercero` (clientes/proveedores/ambos)
   - ✅ Modelo `Impuesto` (IVA, ICA, etc.)
   - ✅ Modelo `MetodoPago` (efectivo, transferencia, tarjeta)
   - ✅ Modelo `Producto` (inventario básico)
   - ✅ Vistas CBV (ListView, DetailView, CreateView, UpdateView, DeleteView)
   - ⚠️ Templates básicos creados PERO necesitan mejora UX/UI

5. **Módulo de Contabilidad:**
   - ✅ Modelo `CuentaContable` (plan de cuentas PUC Colombia)
   - ✅ Modelo `Asiento` (asientos contables)
   - ✅ Modelo `Partida` (débito/crédito de asientos)
   - ✅ Servicio `ServicioPlanCuentas` (crear plan básico)
   - ✅ Servicio `ServicioContabilidad` (generar asientos automáticos)
   - ✅ Vistas CBV básicas
   - ⚠️ Templates básicos PERO funcionalidad avanzada pendiente

6. **Módulo de Facturación:**
   - ✅ Modelo `Factura` (facturas de venta)
   - ✅ Modelo `FacturaDetalle` (líneas de factura)
   - ✅ Relación con asientos contables
   - ✅ Estados: borrador/confirmada/anulada
   - ✅ Vistas CBV básicas
   - ❌ Lógica de negocio avanzada PENDIENTE
   - ❌ Generación automática de asientos PENDIENTE
   - ❌ PDF/impresión PENDIENTE
   - ❌ Templates funcionales PENDIENTES

7. **Módulo de Tesorería:**
   - ✅ Modelo `Pago` (pagos/cobros/egresos)
   - ✅ Modelo `CuentaBancaria`
   - ✅ Relación con facturas y asientos
   - ✅ Vistas CBV básicas
   - ⚠️ Templates básicos (algunos creados en rama Gabo)
   - ❌ Flujo de caja PENDIENTE
   - ❌ Conciliación bancaria PENDIENTE

8. **Módulo de Reportes:**
   - ✅ Modelo `ReporteGenerado`
   - ✅ Modelo `ConfiguracionReporte`
   - ✅ URLs y vistas CBV para:
     - Libro Diario
     - Libro Mayor
     - Balance de Comprobación
     - Estado de Resultados
     - Balance General
     - Flujo de Efectivo
   - ❌ Lógica de generación PENDIENTE
   - ❌ Exportación a PDF/Excel PENDIENTE
   - ❌ Templates funcionales PENDIENTES

#### ⚠️ **EN PROGRESO / PARCIAL**
- Templates de catálogos (existen pero mejorar UX)
- Templates de facturación (estructura básica)
- Templates de tesorería (algunos en rama Gabo)
- Templates de reportes (estructura básica)
- Lógica de negocio avanzada en módulos transaccionales

#### ❌ **PENDIENTE / NO INICIADO**
- Tests unitarios completos
- Documentación de usuario final
- Funciones avanzadas de reportes
- Integración completa contabilidad↔facturación↔tesorería
- Validaciones de negocio complejas
- Optimizaciones de rendimiento
- Despliegue a producción

---

## 👥 DIVISIÓN EQUITATIVA DEL TRABAJO

### 🔵 **RAMA: wiki** → Administrador (Wiki)
**Responsabilidad:** Módulo de Empresas y Administración del Holding

#### 📦 Tareas Asignadas:

**1. Garantizar calidad del módulo de Empresas (YA HECHO - revisar/mejorar):**
- [ ] Revisar y probar exhaustivamente el dashboard del administrador
- [ ] Verificar CRUD de empresas (crear, editar, ver, eliminar)
- [ ] Verificar CRUD de usuarios
- [ ] Probar asignación de usuarios a empresas con roles
- [ ] Revisar sistema de historial de cambios
- [ ] Probar exportación de historial a CSV
- [ ] Validar estadísticas del holding
- [ ] Revisar middleware de historial
- [ ] Documentar flujos de trabajo del administrador

**2. Mejorar y completar funcionalidades administrativas:**
- [ ] Añadir filtros avanzados en gestión de empresas
- [ ] Añadir búsqueda en gestión de usuarios
- [ ] Implementar paginación optimizada
- [ ] Añadir bulk actions (activar/desactivar múltiples usuarios)
- [ ] Crear dashboard de métricas avanzadas (gráficos)
- [ ] Implementar notificaciones para administrador
- [ ] Añadir sistema de permisos granular (opcional)
- [ ] Mejorar UX/UI de templates administrativos

**3. Integración con otros módulos:**
- [ ] Validar que el cambio de empresa activa funcione en TODOS los módulos
- [ ] Asegurar que los permisos se respeten en facturación/tesorería/reportes
- [ ] Crear middleware de auditoría avanzada (quién hizo qué y cuándo)

**4. Tests y Documentación:**
- [ ] Crear tests unitarios para models de empresas
- [ ] Crear tests de vistas del administrador
- [ ] Documentar manual de administrador (con capturas)
- [ ] Crear guía de troubleshooting común

#### 📁 Archivos Principales:
```
empresas/
├── models.py (Empresa, PerfilEmpresa, HistorialCambios)
├── views_admin.py (todas las vistas de administrador)
├── middleware_historial.py
├── utils_historial.py
├── admin.py
└── templates/empresas/admin/
    ├── dashboard_admin.html
    ├── gestionar_empresas.html
    ├── gestionar_usuarios.html
    ├── empresa_form.html
    ├── usuario_form.html
    ├── asignar_usuario.html
    ├── estadisticas.html
    └── historial_cambios.html
```

#### 🎯 Objetivo: Módulo administrativo robusto, bien probado y documentado.

---

### 🟢 **RAMA: Gabo** → Facturación y Ventas (Gabo)
**Responsabilidad:** Módulo de Facturación completo y funcional

#### 📦 Tareas Asignadas:

**1. Completar lógica de negocio de Facturación:**
- [ ] Implementar función `confirmar_factura()` (cambiar estado a confirmada)
- [ ] Implementar función `anular_factura()` (cambiar estado a anulada)
- [ ] Implementar función `duplicar_factura()` (clonar factura existente)
- [ ] Añadir validaciones de negocio:
  - Validar stock de productos al crear factura
  - Validar límite de crédito de clientes
  - Validar cálculos de impuestos
  - Validar totales (subtotal + impuestos = total)

**2. Integración con Contabilidad:**
- [ ] Al confirmar factura → generar asiento contable automático
  - Débito: Clientes (1305 PUC)
  - Crédito: Ingresos (4135 PUC)
  - Crédito: IVA generado (2408 PUC)
- [ ] Al anular factura → reversar asiento contable
- [ ] Probar integración con `ServicioContabilidad`

**3. Templates funcionales y UX:**
- [ ] Crear/mejorar `factura_list.html` (listado con filtros)
- [ ] Crear/mejorar `factura_form.html` (crear/editar con líneas dinámicas)
- [ ] Crear/mejorar `factura_detail.html` (ver factura completa)
- [ ] Implementar JavaScript para:
  - Añadir/eliminar líneas de factura dinámicamente
  - Calcular totales en tiempo real
  - Autocompletar productos
  - Validación del lado del cliente
- [ ] Diseñar interfaz responsive (móvil/tablet/desktop)

**4. Generación de PDF e Impresión:**
- [ ] Implementar `factura_pdf()` usando ReportLab o WeasyPrint
- [ ] Diseñar template de factura profesional (logo, datos empresa, etc.)
- [ ] Implementar `factura_imprimir()` (versión para impresora térmica)
- [ ] Añadir botón "Descargar PDF" en detalle de factura

**5. Reportes y Consultas:**
- [ ] Crear vista de facturas por cliente
- [ ] Crear vista de facturas por período
- [ ] Implementar reporte de ventas (diario/semanal/mensual)
- [ ] Añadir gráficos de ventas (Chart.js o similar)

**6. Tests y Documentación:**
- [ ] Tests unitarios para modelo Factura
- [ ] Tests de integración con contabilidad
- [ ] Tests de generación de PDF
- [ ] Documentar proceso de facturación (manual de usuario)

#### 📁 Archivos Principales:
```
facturacion/
├── models.py (Factura, FacturaDetalle)
├── views.py (completar funciones vacías)
├── services.py (lógica de negocio - CREAR)
├── urls.py
└── templates/facturacion/
    ├── lista.html
    ├── crear.html
    ├── editar.html
    ├── detalle.html
    ├── reporte.html
    └── pdf/
        └── factura_template.html

static/js/
└── facturacion.js (lógica frontend)
```

#### 🎯 Objetivo: Sistema de facturación completo, con generación de asientos contables y PDF.

---

### 🟡 **RAMA: Sneyder** → Tesorería y Flujo de Caja (Sneyder)
**Responsabilidad:** Módulo de Tesorería completo y funcional

#### 📦 Tareas Asignadas:

**1. Completar lógica de negocio de Tesorería:**
- [ ] Implementar función `confirmar_pago()` (cambiar estado y actualizar saldos)
- [ ] Implementar función `anular_pago()` (reversar estado y saldos)
- [ ] Implementar función `cobrar_factura()` (crear cobro desde factura)
- [ ] Añadir validaciones de negocio:
  - Validar saldo de cuenta bancaria para egresos
  - Validar monto de cobro vs saldo pendiente factura
  - Validar método de pago (requiere referencia si es transferencia)

**2. Integración con Contabilidad:**
- [ ] Al confirmar pago/cobro → generar asiento contable automático
  - Cobro: Débito Bancos, Crédito Clientes
  - Pago: Débito Proveedores, Crédito Bancos
  - Egreso: Débito Gastos, Crédito Bancos
- [ ] Al anular → reversar asiento contable
- [ ] Probar integración con `ServicioContabilidad`

**3. Templates funcionales y UX:**
- [ ] Crear/mejorar `pagos_lista.html` (listado con filtros)
- [ ] Crear/mejorar `pagos_form.html` (crear/editar pago)
- [ ] Crear/mejorar `pagos_detalle.html` (ver pago completo)
- [ ] Crear templates de cobros (reutilizar o adaptar)
- [ ] Crear templates de egresos
- [ ] Crear template de cuentas bancarias (CRUD completo)
- [ ] Implementar JavaScript para:
  - Seleccionar factura y autocompletar monto
  - Validar disponibilidad de fondos
  - Calcular saldos en tiempo real

**4. Flujo de Caja:**
- [ ] Implementar vista `flujo_caja.html` (entradas/salidas del período)
- [ ] Calcular saldo inicial, ingresos, egresos, saldo final
- [ ] Añadir filtros por fecha, cuenta bancaria, tipo de movimiento
- [ ] Implementar gráfico de flujo de caja (Chart.js)
- [ ] Añadir proyección de flujo de caja (próximos 30 días)

**5. Conciliación Bancaria:**
- [ ] Crear vista de conciliación bancaria
- [ ] Permitir importar extracto bancario (CSV o manual)
- [ ] Comparar movimientos sistema vs banco
- [ ] Marcar movimientos como conciliados
- [ ] Generar reporte de diferencias

**6. Cuentas Bancarias:**
- [ ] Completar CRUD de cuentas bancarias
- [ ] Implementar dashboard de saldos de cuentas
- [ ] Añadir histórico de movimientos por cuenta
- [ ] Implementar transferencias entre cuentas

**7. Tests y Documentación:**
- [ ] Tests unitarios para modelo Pago y CuentaBancaria
- [ ] Tests de integración con contabilidad
- [ ] Tests de cálculo de flujo de caja
- [ ] Documentar proceso de tesorería (manual de usuario)

#### 📁 Archivos Principales:
```
tesoreria/
├── models.py (Pago, CuentaBancaria)
├── views.py (completar funciones vacías)
├── services.py (lógica de negocio - CREAR)
├── forms.py (formularios - ya existe)
├── urls.py
└── templates/tesoreria/
    ├── index.html
    ├── pagos_lista.html
    ├── pagos_crear.html
    ├── pagos_detalle.html
    ├── cobros_lista.html
    ├── cobros_crear.html
    ├── egresos_lista.html
    ├── egresos_crear.html
    ├── cuentas_lista.html
    ├── cuentas_detalle.html
    ├── flujo_caja.html
    ├── saldos_cuentas.html
    └── conciliacion.html

static/js/
└── tesoreria.js (lógica frontend)
```

#### 🎯 Objetivo: Sistema de tesorería completo con flujo de caja y conciliación bancaria.

---

### 🟣 **RAMA: Estiven** → Reportes Contables y Catálogos (Estiven)
**Responsabilidad:** Módulo de Reportes completo + mejorar Catálogos

#### 📦 Tareas Asignadas:

**1. Completar Módulo de Reportes Contables:**

**a) Libro Diario:**
- [ ] Implementar `generar_libro_diario()` (consultar asientos del período)
- [ ] Calcular totales de débitos y créditos
- [ ] Implementar template `diario.html` con tabla de asientos
- [ ] Implementar `exportar_libro_diario()` (PDF y Excel)

**b) Libro Mayor:**
- [ ] Implementar `generar_libro_mayor()` (consultar movimientos por cuenta)
- [ ] Calcular saldos acumulados por cuenta
- [ ] Implementar template `mayor.html` (lista de cuentas con saldo)
- [ ] Implementar template `mayor_cuenta.html` (detalle de movimientos)
- [ ] Implementar `exportar_libro_mayor()` (PDF y Excel)

**c) Balance de Comprobación:**
- [ ] Implementar `generar_balance_comprobacion()` (sumas y saldos)
- [ ] Calcular débitos, créditos y saldos por cuenta
- [ ] Verificar que débitos = créditos (cuadre contable)
- [ ] Implementar template `balance_comprobacion.html`
- [ ] Implementar `exportar_balance_comprobacion()` (PDF y Excel)

**d) Estado de Resultados (P&G):**
- [ ] Implementar `generar_estado_resultados()` (ingresos - gastos)
- [ ] Clasificar cuentas en:
  - Ingresos operacionales (clase 4)
  - Gastos operacionales (clase 5)
  - Otros ingresos/gastos (clase 6)
- [ ] Calcular utilidad/pérdida del período
- [ ] Implementar template `estado_resultados.html`
- [ ] Implementar `exportar_estado_resultados()` (PDF y Excel)
- [ ] Añadir comparativa con períodos anteriores (opcional)

**e) Balance General:**
- [ ] Implementar `generar_balance_general()` (activos/pasivos/patrimonio)
- [ ] Clasificar cuentas en:
  - Activos (clase 1)
  - Pasivos (clase 2)
  - Patrimonio (clase 3)
- [ ] Verificar ecuación contable: Activos = Pasivos + Patrimonio
- [ ] Implementar template `balance_general.html`
- [ ] Implementar `exportar_balance_general()` (PDF y Excel)

**f) Flujo de Efectivo:**
- [ ] Implementar `generar_flujo_efectivo()` (método directo o indirecto)
- [ ] Clasificar movimientos de efectivo en:
  - Actividades operativas
  - Actividades de inversión
  - Actividades de financiación
- [ ] Calcular variación neta de efectivo
- [ ] Implementar template `flujo_efectivo.html`
- [ ] Implementar `exportar_flujo_efectivo()` (PDF y Excel)

**2. Configuraciones y Utilidades:**
- [ ] Implementar guardado de configuraciones de reportes
- [ ] Permitir programar generación automática de reportes
- [ ] Añadir validación de períodos contables
- [ ] Implementar preview de reportes antes de exportar

**3. Mejorar Módulo de Catálogos:**

**a) Terceros (Clientes/Proveedores):**
- [ ] Mejorar template `tercero_list.html` (añadir filtros)
- [ ] Mejorar template `tercero_form.html` (validaciones frontend)
- [ ] Añadir importación masiva de terceros (CSV/Excel)
- [ ] Implementar búsqueda avanzada (por NIT, nombre, tipo)
- [ ] Añadir vista de estado de cuenta de tercero

**b) Productos:**
- [ ] Mejorar template `productos_lista.html` (añadir imágenes)
- [ ] Mejorar template `productos_crear.html` (campos adicionales)
- [ ] Implementar control de inventario básico
- [ ] Añadir alertas de stock mínimo
- [ ] Implementar búsqueda rápida de productos (AJAX)

**c) Impuestos:**
- [ ] Validar configuración de impuestos (porcentajes válidos)
- [ ] Añadir soporte para múltiples impuestos en un producto
- [ ] Implementar cálculo automático en facturación

**d) Métodos de Pago:**
- [ ] Completar CRUD (ya existe estructura básica)
- [ ] Validar configuración de métodos (requiere referencia, etc.)

**4. Tests y Documentación:**
- [ ] Tests de generación de reportes (datos de prueba)
- [ ] Tests de exportación PDF/Excel
- [ ] Tests de módulo catálogos
- [ ] Documentar reportes contables (interpretación)
- [ ] Crear manual de catálogos (cómo registrar terceros, productos, etc.)

#### 📁 Archivos Principales:
```
reportes/
├── models.py (ReporteGenerado, ConfiguracionReporte)
├── views.py (completar todas las funciones de generación)
├── services.py (lógica de reportes - CREAR)
├── utils.py (funciones de exportación PDF/Excel - CREAR)
├── urls.py
└── templates/reportes/
    ├── index.html
    ├── diario.html
    ├── mayor.html
    ├── mayor_cuenta.html
    ├── balance_comprobacion.html
    ├── estado_resultados.html
    ├── balance_general.html
    ├── flujo_efectivo.html
    ├── configuraciones_lista.html
    └── historial.html

catalogos/
├── models.py (Tercero, Producto, Impuesto, MetodoPago)
├── views.py (mejorar vistas existentes)
├── forms.py (CREAR - formularios avanzados)
├── urls.py
└── templates/catalogos/
    ├── tercero_list.html (mejorar)
    ├── tercero_form.html (mejorar)
    ├── tercero_detalle.html (mejorar)
    ├── productos_lista.html (mejorar)
    ├── productos_crear.html (mejorar)
    ├── impuestos_*.html (mejorar)
    └── metodos_pago_*.html (mejorar)

static/js/
├── reportes.js (lógica frontend)
└── catalogos.js (búsquedas AJAX, validaciones)
```

#### 🎯 Objetivo: Sistema de reportes contables completo con exportación PDF/Excel + catálogos funcionales.

---

## 📊 RESUMEN DE DISTRIBUCIÓN

| Desarrollador | Módulos Principales | Módulos Secundarios | Complejidad | Horas Estimadas |
|---------------|---------------------|---------------------|-------------|-----------------|
| **Wiki** | Empresas + Administración | Middleware, Permisos | ⭐⭐⭐ Media | ~40-50 horas |
| **Gabo** | Facturación + Ventas | PDF, Integración Contabilidad | ⭐⭐⭐⭐ Alta | ~50-60 horas |
| **Sneyder** | Tesorería + Flujo Caja | Conciliación, Cuentas Bancarias | ⭐⭐⭐⭐ Alta | ~50-60 horas |
| **Estiven** | Reportes Contables + Catálogos | Exportación PDF/Excel | ⭐⭐⭐⭐⭐ Muy Alta | ~60-70 horas |

---

## 🔄 FLUJO DE TRABAJO RECOMENDADO

### 1. Branching Strategy
```bash
# Cada desarrollador trabaja en su rama
git checkout wiki      # Wiki en su rama
git checkout Gabo      # Gabo en su rama
git checkout sneyder   # Sneyder en su rama
git checkout Estiven   # Estiven en su rama

# Hacer commits frecuentes
git add .
git commit -m "feat: descripción clara del cambio"
git push origin [tu-rama]

# Sincronizar con master regularmente
git checkout master
git pull origin master
git checkout [tu-rama]
git merge master
```

### 2. Reuniones de Coordinación
- **Daily standup (10 min):** ¿Qué hice ayer? ¿Qué haré hoy? ¿Tengo bloqueos?
- **Weekly review (30 min):** Demo de avances, resolver dependencias entre módulos
- **Code review:** Cada uno revisa PRs de otros (mínimo 1 aprobación para merge)

### 3. Dependencias entre Módulos
- **Gabo (Facturación)** depende de:
  - Estiven (Catálogos) → productos, terceros, impuestos
  - Contabilidad (ya existe) → generar asientos
- **Sneyder (Tesorería)** depende de:
  - Gabo (Facturación) → cobrar facturas
  - Estiven (Catálogos) → métodos de pago, terceros
  - Contabilidad → generar asientos
- **Estiven (Reportes)** depende de:
  - Contabilidad (ya existe) → leer asientos
  - Catálogos → filtros de reportes
- **Wiki (Administración)** es independiente (ya está hecho)

**Recomendación:** Estiven debe priorizar completar Catálogos primero para desbloquear a Gabo y Sneyder.

### 4. Criterios de Aceptación (Definition of Done)
Para considerar una tarea completada:
- [ ] Código implementado y funcionando
- [ ] Templates HTML funcionales y responsive
- [ ] Validaciones de negocio implementadas
- [ ] Integración con otros módulos probada
- [ ] Al menos 2 tests unitarios/integración
- [ ] Comentarios en código complejo
- [ ] Sin errores de SonarCloud críticos
- [ ] PR revisado y aprobado por al menos 1 compañero
- [ ] Documentación básica en README o documento técnico

---

## 📅 CRONOGRAMA SUGERIDO (4 semanas)

### Semana 1: Fundamentos y Bases
- **Todos:** Leer y entender el código base
- **Wiki:** Revisar y documentar módulo de empresas
- **Estiven:** Completar Catálogos (Terceros, Productos) → PRIORIDAD
- **Gabo:** Diseñar templates de facturación
- **Sneyder:** Diseñar templates de tesorería

### Semana 2: Desarrollo Core
- **Wiki:** Mejorar UX/UI administrador, añadir filtros
- **Estiven:** Terminar Catálogos y empezar Libro Diario/Mayor
- **Gabo:** Implementar lógica de facturación (confirmar, anular)
- **Sneyder:** Implementar lógica de tesorería (pagos, cobros)

### Semana 3: Integración y Reportes
- **Wiki:** Tests y documentación de administración
- **Estiven:** Completar todos los reportes contables
- **Gabo:** Integración con contabilidad + generación de PDF
- **Sneyder:** Flujo de caja + conciliación bancaria

### Semana 4: Pulido y Testing
- **Todos:** Tests unitarios y de integración
- **Todos:** Code review cruzado
- **Todos:** Documentación de usuario final
- **Todos:** Demo final y ajustes

---

## 🛠️ HERRAMIENTAS Y RECURSOS

### Librerías Recomendadas
```bash
# Generación de PDF
pip install reportlab weasyprint

# Exportación a Excel
pip install openpyxl xlsxwriter

# Gráficos (frontend)
# Usar Chart.js (ya incluir en CDN en templates)

# Tests
pip install pytest pytest-django pytest-cov
```

### Comandos Útiles
```powershell
# Activar entorno virtual
.\env\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Correr servidor
python manage.py runserver

# Correr tests
python manage.py test [app_name]

# Análisis de código
# (automático en GitHub Actions con SonarCloud)
```

### Recursos de Aprendizaje
- **Django Docs:** https://docs.djangoproject.com/
- **DRF Docs:** https://www.django-rest-framework.org/
- **PUC Colombia:** https://www.ctcp.gov.co/ (plan de cuentas)
- **Chart.js:** https://www.chartjs.org/
- **ReportLab:** https://www.reportlab.com/docs/reportlab-userguide.pdf

---

## 🎯 OBJETIVOS FINALES DEL PROYECTO

Al completar todas las tareas, el sistema debe:
1. ✅ Permitir gestionar múltiples empresas (holding)
2. ✅ Permitir crear usuarios y asignarlos a empresas con roles
3. ✅ Registrar clientes, proveedores, productos
4. ✅ Facturar ventas con cálculo automático de impuestos
5. ✅ Generar asientos contables automáticos
6. ✅ Gestionar pagos, cobros y egresos
7. ✅ Controlar flujo de caja en tiempo real
8. ✅ Generar reportes contables (Libro Diario, Mayor, Balances, P&G)
9. ✅ Exportar reportes a PDF y Excel
10. ✅ Tener API REST funcional con autenticación JWT

---

## 📞 CONTACTO Y SOPORTE

**Coordinador del Proyecto:** [Tu nombre]  
**Repositorio:** https://github.com/JUANESTEBANORTIZRENDON/FinalPoo2  
**SonarCloud:** https://sonarcloud.io (proyecto: JEYomboy_FinalPoo2)  
**Documentación:** Ver archivos README.md y esta división de trabajo

---

## ✅ CHECKLIST DE ENTREGA FINAL

### Por Desarrollador:
- [ ] **Wiki:** Módulo de administración documentado y probado
- [ ] **Gabo:** Facturación completa con PDF e integración contable
- [ ] **Sneyder:** Tesorería completa con flujo de caja
- [ ] **Estiven:** Reportes contables completos + catálogos funcionales

### General:
- [ ] Todos los PRs mergeados a `master`
- [ ] Migraciones aplicadas sin conflictos
- [ ] Tests con cobertura mínima 60%
- [ ] SonarCloud Quality Gate: PASSED
- [ ] README.md actualizado con instrucciones de despliegue
- [ ] Documentación de usuario final
- [ ] Demo funcional lista para presentación

---

**Fecha de Creación:** 5 de Noviembre de 2025  
**Última Actualización:** 5 de Noviembre de 2025  
**Versión:** 1.0

---

## 💡 NOTAS IMPORTANTES

1. **Comunicación:** Usen el grupo de chat del equipo para coordinar cambios que afecten a otros.
2. **Conflictos de merge:** Si tienen conflictos, avisen al grupo y resuelvan juntos.
3. **Prioridades:** Estiven debe completar Catálogos primero (desbloquea a Gabo y Sneyder).
4. **Calidad:** Prefieran código limpio y bien testeado sobre cantidad de funcionalidades.
5. **Git:** Hagan commits pequeños y frecuentes con mensajes claros.
6. **SonarCloud:** Revisen los issues de SonarCloud y corríjanlos antes de merge.
7. **Ayuda mutua:** Si terminas tus tareas antes, ayuda a tus compañeros.

**¡Éxito en el proyecto! 🚀**
