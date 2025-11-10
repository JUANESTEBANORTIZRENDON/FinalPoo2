# 📚 GUÍA COMPLETA DE MODELOS - PANEL DESARROLLADOR

## 🎯 Introducción

Este documento describe en detalle **todos los modelos** disponibles en el **Panel Desarrollador** de S_CONTABLE. Cada sección explica el propósito, funcionalidad y diferencias entre modelos con nombres similares.

---

## 📑 Índice de Secciones

1. [Gestión de Usuarios](#1-gestión-de-usuarios)
2. [Empresas](#2-empresas)
3. [Catálogos](#3-catálogos)
4. [Otros Modelos del Sistema](#4-otros-modelos-del-sistema)

---

# 1. GESTIÓN DE USUARIOS

## 📊 Estructura General

La gestión de usuarios en S_CONTABLE se divide en **3 componentes principales**:

```
User (Django Auth)
    ↓
PerfilUsuario (Extensión personalizada)
    ↓
Grupos y Permisos
```

---

## 👤 1.1. Usuarios (User)

### 🎯 Propósito
Modelo **base de Django** para autenticación y autorización. Es el núcleo del sistema de usuarios.

### 📋 Funcionalidad
- **Autenticación**: Login/logout del sistema
- **Autorización**: Permisos y grupos
- **Identificación única**: Username y email
- **Seguridad**: Contraseñas hasheadas
- **Auditoría**: Fechas de creación y último login

### 🔑 Campos Principales
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `username` | String | Nombre de usuario único (login) |
| `email` | Email | Correo electrónico |
| `first_name` | String | Nombre(s) |
| `last_name` | String | Apellido(s) |
| `password` | Hash | Contraseña encriptada |
| `is_active` | Boolean | Usuario activo/inactivo |
| `is_staff` | Boolean | Puede acceder al admin |
| `is_superuser` | Boolean | Tiene todos los permisos |
| `date_joined` | DateTime | Fecha de registro |
| `last_login` | DateTime | Último inicio de sesión |

### 🎬 Casos de Uso
1. **Login**: Autenticación de usuarios en el sistema
2. **Gestión de permisos**: Asignar roles (admin, contador, operador)
3. **Auditoría**: Rastrear quién hizo qué en el sistema
4. **Control de acceso**: Activar/desactivar cuentas

### 🔗 Relaciones
- **1:1** con `PerfilUsuario` (extensión de datos)
- **N:M** con `Group` (roles/grupos)
- **N:M** con `Permission` (permisos individuales)
- **1:N** con `EmpresaActiva` (empresas asignadas)
- **1:N** con `HistorialCambios` (acciones realizadas)

---

## 📝 1.2. Perfiles de Usuarios (PerfilUsuario)

### 🎯 Propósito
**Extensión del modelo User** con información adicional específica para el sistema contable colombiano.

### ❓ ¿Por qué existe si ya hay User?

**User** es genérico y limitado. **PerfilUsuario** agrega:
- ✅ Datos de identificación colombiana (CC, CE, NIT)
- ✅ Información personal completa
- ✅ Datos laborales y profesionales
- ✅ Configuraciones personalizadas
- ✅ Campos específicos del negocio

### 📋 Funcionalidad
- **Identificación legal**: Tipos de documento colombianos
- **Datos personales**: Género, estado civil, fecha de nacimiento
- **Ubicación**: Dirección completa, ciudad, departamento
- **Contacto**: Teléfono celular colombiano
- **Profesional**: Profesión, cargo, experiencia
- **Sistema**: Avatar, biografía, configuraciones

### 🔑 Campos Principales

#### Identificación
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `usuario` | FK(User) | Relación 1:1 con User |
| `tipo_documento` | Choice | CC, CE, TI, PP, NIT |
| `numero_documento` | String | Número sin puntos (único) |

#### Información Personal
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `fecha_nacimiento` | Date | Fecha de nacimiento |
| `genero` | Choice | M, F, O, N |
| `estado_civil` | Choice | S, C, U, D, V |

#### Contacto y Ubicación
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `telefono` | String | Formato colombiano +57... |
| `direccion` | Text | Dirección completa |
| `ciudad` | String | Ciudad de residencia |
| `departamento` | String | Departamento (Cundinamarca, etc) |
| `codigo_postal` | String | Código postal |

#### Información Profesional
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `profesion` | String | Contador, Administrador, etc |
| `cargo` | String | Puesto en la empresa |
| `anos_experiencia` | Integer | Años de experiencia |
| `tarjeta_profesional` | String | Número de TP (contadores) |

#### Personalización
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `avatar` | Image | Foto de perfil |
| `biografia` | Text | Descripción personal |
| `preferencias` | JSON | Configuraciones del usuario |

### 🎬 Casos de Uso
1. **Registro completo**: Capturar datos legales y personales
2. **Verificación de identidad**: Validar documentos colombianos
3. **Perfilamiento**: Adaptar sistema según profesión
4. **Contacto**: Comunicación con usuarios
5. **Cumplimiento legal**: Datos requeridos para auditorías

### 🔗 Relaciones
- **1:1** con `User` (required)
- **N:1** con empresas (a través de EmpresaActiva)

---

## 👥 1.3. Grupos (Group)

### 🎯 Propósito
**Sistema de roles** para organizar usuarios y asignar permisos en conjunto.

### 📋 Funcionalidad
- **Agrupación lógica**: Contadores, Administradores, Operadores
- **Permisos masivos**: Asignar permisos a múltiples usuarios
- **Jerarquía de acceso**: Definir niveles de autorización
- **Escalabilidad**: Fácil gestión de permisos

### 🔑 Grupos Predefinidos en S_CONTABLE

#### 🏆 Administrador
- **Acceso total** al sistema
- Puede gestionar empresas, usuarios y configuraciones
- Acceso al Panel Desarrollador

#### 🧮 Contador
- Gestión completa de contabilidad
- Acceso a registros contables, reportes y cierres
- **NO** puede gestionar usuarios ni empresas

#### 🔧 Operador
- Captura de documentos y transacciones
- **NO** puede aprobar o cerrar períodos
- Acceso limitado a consultas

#### 👁️ Observador
- **Solo lectura** de información
- Consulta de reportes y estados
- **NO** puede modificar datos

### 🎬 Casos de Uso
1. **Onboarding**: Asignar rol al registrar usuario
2. **Control de acceso**: Limitar funcionalidades por rol
3. **Delegación**: Cambiar roles según necesidades
4. **Auditoría**: Rastrear acciones por grupo

### 🔗 Relaciones
- **N:M** con `User` (usuarios pueden tener múltiples grupos)
- **N:M** con `Permission` (permisos del grupo)

---

## 🔐 1.4. Permisos (Permission)

### 🎯 Propósito
**Control granular de acceso** a funcionalidades específicas del sistema.

### 📋 Funcionalidad
- **CRUD detallado**: view, add, change, delete por modelo
- **Permisos personalizados**: Acciones específicas del negocio
- **Seguridad**: Prevenir accesos no autorizados
- **Flexibilidad**: Combinar con grupos

### 🔑 Tipos de Permisos

#### Permisos Estándar (por modelo)
| Permiso | Código | Descripción |
|---------|--------|-------------|
| View | `view_<modelo>` | Ver registros |
| Add | `add_<modelo>` | Crear nuevos |
| Change | `change_<modelo>` | Editar existentes |
| Delete | `delete_<modelo>` | Eliminar registros |

#### Permisos Personalizados
| Permiso | Descripción |
|---------|-------------|
| `cerrar_periodo_contable` | Cerrar mes contable |
| `aprobar_factura` | Aprobar facturas |
| `acceder_reportes_financieros` | Ver estados financieros |
| `gestionar_holding` | Administrar empresas del holding |

### 🎬 Casos de Uso
1. **Separación de funciones**: Contadores aprueban, operadores capturan
2. **Cumplimiento**: Auditores solo consultan
3. **Seguridad**: Restringir eliminaciones
4. **Flujos de aprobación**: Validaciones por niveles

---

# 2. EMPRESAS

## 📊 Estructura General

```
Empresa (Datos maestros)
    ↓
PerfilEmpresa (Extensión - FUTURO)
    ↓
EmpresaActiva (Asignación Usuario-Empresa)
    ↓
HistorialCambios (Auditoría)
```

---

## 🏢 2.1. Empresas (Empresa)

### 🎯 Propósito
**Modelo principal** para gestionar empresas en el sistema contable. Cada empresa tiene su propia contabilidad independiente.

### 📋 Funcionalidad
- **Registro legal**: NIT, razón social, tipo de empresa
- **Tributación**: Régimen, responsabilidades fiscales
- **Multi-empresa**: Soporte para holdings y grupos empresariales
- **Contacto**: Ubicación y datos de comunicación
- **Configuración contable**: Moneda, año fiscal

### 🔑 Campos Principales

#### Identificación Legal
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `nit` | String | NIT con DV (123456789-0) |
| `razon_social` | String | Nombre legal de la empresa |
| `nombre_comercial` | String | Nombre público (opcional) |
| `tipo_empresa` | Choice | SAS, LTDA, SA, ESAL, Persona Natural |

#### Información Tributaria
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `regimen_tributario` | Choice | Común, Simplificado, Especial |
| `responsable_iva` | Boolean | ¿Cobra IVA? |
| `gran_contribuyente` | Boolean | ¿Es gran contribuyente? |
| `autorretenedor` | Boolean | ¿Practica autorretención? |

#### Contacto
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `direccion` | Text | Dirección fiscal |
| `ciudad` | String | Ciudad |
| `departamento` | String | Departamento |
| `telefono` | String | Teléfono corporativo |
| `email` | Email | Email institucional |
| `sitio_web` | URL | Página web (opcional) |

#### Configuración Contable
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `moneda_base` | String | COP (pesos colombianos) |
| `ano_fiscal_inicio` | Integer | Mes de inicio (1-12) |
| `digitos_cuenta` | Integer | Longitud del PUC |

#### Control
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `activa` | Boolean | Empresa operativa |
| `fecha_constitucion` | Date | Fecha de creación legal |
| `fecha_registro` | DateTime | Registro en el sistema |
| `ultima_actualizacion` | DateTime | Última modificación |

### 🎬 Casos de Uso
1. **Multi-empresa**: Gestionar varias empresas desde una cuenta
2. **Holding**: Administrar grupo empresarial
3. **Contadores externos**: Un contador para múltiples clientes
4. **Segregación**: Contabilidad independiente por empresa

### 🔗 Relaciones
- **1:N** con `EmpresaActiva` (usuarios asignados)
- **1:N** con transacciones contables
- **1:N** con `HistorialCambios` (auditoría)
- **1:1** con `PerfilEmpresa` (futuro)

---

## 📋 2.2. Perfiles de Empresas en Empresas (PerfilEmpresa)

### 🎯 Propósito
**Extensión futura** del modelo Empresa para datos adicionales no críticos.

### ❓ ¿Por qué existe si ya hay Empresa?

**Empresa** contiene datos **críticos y legales**. **PerfilEmpresa** es para:
- ✅ Información complementaria
- ✅ Datos de marketing
- ✅ Configuraciones avanzadas
- ✅ Integraciones externas

### 📋 Funcionalidad Planeada
- **Datos comerciales**: Descripción, sector, tamaño
- **Redes sociales**: Links a perfiles
- **Representante legal**: Datos del gerente
- **Configuraciones**: Preferencias de reportes
- **Integraciones**: API keys, webhooks

### 🔑 Campos Planeados
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `empresa` | FK(Empresa) | Relación 1:1 |
| `descripcion` | Text | Descripción de la empresa |
| `sector_economico` | Choice | Sector CIIU |
| `numero_empleados` | Integer | Tamaño de la empresa |
| `logo` | Image | Logo corporativo |
| `representante_legal` | String | Nombre del representante |
| `facebook` | URL | Perfil de Facebook |
| `instagram` | URL | Perfil de Instagram |
| `linkedin` | URL | Perfil de LinkedIn |

### 🎬 Casos de Uso (Futuro)
1. **Perfil público**: Mostrar información comercial
2. **Categorización**: Filtrar por sector o tamaño
3. **Integraciones**: Conectar con servicios externos
4. **Branding**: Logo y colores personalizados

### ⚠️ Estado Actual
**MODELO PREPARADO PERO NO IMPLEMENTADO**
- Estructura definida en `models.py`
- Registrado en `admin.py`
- **Sin datos** actualmente
- Listo para uso futuro

---

## 🔄 2.3. Empresas Activas por Usuario (EmpresaActiva)

### 🎯 Propósito
**Tabla de relación** entre usuarios y empresas. Define qué empresas puede gestionar cada usuario.

### 📋 Funcionalidad
- **Asignación**: Vincular usuarios a empresas
- **Multi-acceso**: Un usuario puede tener varias empresas
- **Control de sesión**: Empresa activa actual del usuario
- **Roles por empresa**: Permisos diferentes en cada empresa
- **Auditoría**: Rastrear asignaciones

### 🔑 Campos Principales
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `usuario` | FK(User) | Usuario asignado |
| `empresa` | FK(Empresa) | Empresa asignada |
| `rol` | Choice | admin, contador, operador, observador |
| `es_principal` | Boolean | ¿Es la empresa predeterminada? |
| `activa_en_sesion` | Boolean | ¿Está activa ahora? |
| `fecha_asignacion` | DateTime | Cuándo se asignó |
| `asignado_por` | FK(User) | Quién hizo la asignación |

### 🎬 Casos de Uso
1. **Contador externo**: Gestiona 10 clientes/empresas
2. **Cambio de empresa**: Usuario cambia de contexto
3. **Permisos por empresa**: Admin en una, operador en otra
4. **Onboarding**: Asignar empresa a nuevo usuario
5. **Revocación**: Quitar acceso a empresa específica

### 🔗 Relaciones
- **N:1** con `User` (un usuario, muchas empresas)
- **N:1** con `Empresa` (una empresa, muchos usuarios)
- **1:N** con sesiones de trabajo

### 💡 Ejemplo Práctico
```
Usuario: Juan Pérez (Contador)
├── Empresa A (Admin) - Principal ✓
├── Empresa B (Contador)
└── Empresa C (Observador)

Empresa activa: Empresa A
```

---

## 📜 2.4. Historial de Cambios (HistorialCambios)

### 🎯 Propósito
**Sistema de auditoría** que registra TODAS las modificaciones importantes en el sistema.

### 📋 Funcionalidad
- **Trazabilidad**: Quién, qué, cuándo, dónde
- **Auditoría**: Cumplimiento normativo
- **Recuperación**: Rastrear errores
- **Seguridad**: Detectar accesos no autorizados
- **Reportes**: Análisis de actividad

### 🔑 Campos Principales
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `usuario` | FK(User) | Quién hizo el cambio |
| `empresa` | FK(Empresa) | En qué empresa |
| `accion` | Choice | CREATE, UPDATE, DELETE, LOGIN, etc |
| `modelo` | String | Qué modelo se modificó |
| `objeto_id` | Integer | ID del registro modificado |
| `descripcion` | Text | Descripción del cambio |
| `cambios_json` | JSON | Valores antes/después |
| `ip_address` | IP | Dirección IP del usuario |
| `user_agent` | String | Navegador/dispositivo |
| `timestamp` | DateTime | Cuándo ocurrió |

### 🎬 Casos de Uso
1. **Auditoría externa**: Mostrar cambios a auditores
2. **Investigación**: "¿Quién eliminó esta factura?"
3. **Cumplimiento**: NIIF requiere trazabilidad
4. **Seguridad**: Detectar actividad sospechosa
5. **Estadísticas**: Análisis de uso del sistema

### 🔗 Relaciones
- **N:1** con `User` (quién)
- **N:1** con `Empresa` (dónde)
- **Generic FK** con cualquier modelo (qué)

### 💡 Ejemplo de Registro
```json
{
  "usuario": "juan.perez",
  "empresa": "ABC S.A.S.",
  "accion": "UPDATE",
  "modelo": "Factura",
  "objeto_id": 12345,
  "descripcion": "Cambió el total de la factura",
  "cambios": {
    "total_antes": "1000000",
    "total_despues": "1200000"
  },
  "ip": "192.168.1.100",
  "timestamp": "2025-11-10 14:30:00"
}
```

---

# 3. CATÁLOGOS

Los catálogos son **tablas maestras** que almacenan información de referencia utilizada en todo el sistema.

---

## 🏪 3.1. Terceros (Tercero)

### 🎯 Propósito
**Gestión de clientes, proveedores y otros terceros** con quienes la empresa realiza transacciones.

### 📋 Funcionalidad
- **Clientes**: Quienes compran productos/servicios
- **Proveedores**: Quienes venden a la empresa
- **Ambos**: Pueden ser cliente y proveedor
- **Contactos**: Información de comunicación
- **Tributación**: Datos fiscales

### 🔑 Campos Principales
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `tipo_identificacion` | Choice | NIT, CC, CE, Pasaporte |
| `numero_identificacion` | String | Documento único |
| `razon_social` | String | Nombre legal/completo |
| `nombre_comercial` | String | Nombre de fantasía |
| `es_cliente` | Boolean | ¿Es cliente? |
| `es_proveedor` | Boolean | ¿Es proveedor? |
| `email` | Email | Email de contacto |
| `telefono` | String | Teléfono |
| `direccion` | Text | Dirección |
| `ciudad` | String | Ciudad |
| `regimen_tributario` | Choice | Común, Simplificado |
| `responsable_iva` | Boolean | ¿Cobra IVA? |

### 🎬 Casos de Uso
1. **Facturación**: Seleccionar cliente al emitir factura
2. **Compras**: Registrar proveedor al recibir factura
3. **Cuentas por cobrar**: Listar clientes con saldo
4. **Cuentas por pagar**: Listar proveedores pendientes
5. **Reportes tributarios**: Medios magnéticos DIAN

---

## 💰 3.2. Impuestos (Impuesto)

### 🎯 Propósito
**Catálogo de impuestos** aplicables en Colombia (IVA, retenciones, etc).

### 📋 Funcionalidad
- **IVA**: 0%, 5%, 19%
- **Retención en la fuente**: Diversos porcentajes
- **ICA**: Impuesto de Industria y Comercio
- **Otros**: Consumo, timbre, etc
- **Cálculos automáticos**: Aplicar % sobre base

### 🔑 Campos Principales
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `codigo` | String | Código interno (IVA19, RTE3.5) |
| `nombre` | String | Nombre descriptivo |
| `tipo` | Choice | IVA, ReteIVA, ReteFuente, ICA |
| `porcentaje` | Decimal | % a aplicar (19.00, 3.50) |
| `activo` | Boolean | ¿Está vigente? |

### 🎬 Casos de Uso
1. **Facturación**: Calcular IVA automáticamente
2. **Retenciones**: Aplicar retención en la fuente
3. **Reportes**: Declaraciones de IVA, retenciones
4. **Configuración**: Actualizar tarifas según DIAN

---

## 💳 3.3. Métodos de Pago (MetodoPago)

### 🎯 Propósito
**Formas de pago** aceptadas por la empresa.

### 📋 Funcionalidad
- **Clasificación**: Efectivo, tarjeta, transferencia, cheque
- **Control**: Habilitar/deshabilitar métodos
- **Reportes**: Análisis por forma de pago
- **Integración**: Pasarelas de pago

### 🔑 Campos Principales
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `codigo` | String | Código único (EFE, TAR, TRA) |
| `nombre` | String | Efectivo, Tarjeta, etc |
| `requiere_banco` | Boolean | ¿Necesita cuenta bancaria? |
| `requiere_aprobacion` | Boolean | ¿Requiere verificación? |
| `activo` | Boolean | ¿Está disponible? |

### 🎬 Casos de Uso
1. **Ventas**: Seleccionar cómo pagó el cliente
2. **Caja**: Conciliación de efectivo vs tarjetas
3. **Bancos**: Movimientos bancarios
4. **Reportes**: Análisis de medios de pago

---

## 📦 3.4. Productos (Producto)

### 🎯 Propósito
**Catálogo de productos y servicios** que la empresa vende.

### 📋 Funcionalidad
- **Inventario**: Control de existencias
- **Precios**: Gestión de tarifas
- **Categorización**: Organizar productos
- **Impuestos**: IVA por producto
- **Facturación**: Listado para facturas

### 🔑 Campos Principales
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `codigo` | String | SKU o código interno |
| `nombre` | String | Nombre del producto |
| `descripcion` | Text | Descripción detallada |
| `tipo` | Choice | Producto, Servicio |
| `categoria` | String | Grupo/categoría |
| `precio_venta` | Decimal | Precio de venta |
| `costo` | Decimal | Costo de adquisición |
| `stock_actual` | Integer | Unidades disponibles |
| `stock_minimo` | Integer | Punto de reorden |
| `impuesto` | FK(Impuesto) | IVA aplicable |
| `activo` | Boolean | ¿Se vende actualmente? |

### 🎬 Casos de Uso
1. **Facturación**: Agregar productos a factura
2. **Inventario**: Control de existencias
3. **Compras**: Registrar adquisiciones
4. **Reportes**: Análisis de ventas por producto
5. **Rentabilidad**: Margen precio-costo

---

# 4. OTROS MODELOS DEL SISTEMA

---

## 💻 4.1. Sesiones (Session)

### 🎯 Propósito
**Gestión de sesiones activas** de usuarios en el sistema.

### 📋 Funcionalidad
- **Autenticación**: Mantener usuario logueado
- **Seguridad**: Expiración de sesiones
- **Multi-dispositivo**: Sesiones simultáneas
- **Auditoría**: Rastrear inicios de sesión

### 🔑 Campos Principales
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `session_key` | String | ID único de sesión |
| `session_data` | Text | Datos de la sesión (encriptados) |
| `expire_date` | DateTime | Cuándo expira |

### 🎬 Casos de Uso
1. **Login persistente**: Mantener sesión activa
2. **Seguridad**: Cerrar sesiones antiguas
3. **Multi-sesión**: Mismo usuario en varios dispositivos
4. **Auditoría**: Rastrear sesiones activas

---

## 🏷️ 4.2. Tipos de Contenido (ContentType)

### 🎯 Propósito
**Metadatos de modelos** del sistema Django. Tabla interna de Django.

### 📋 Funcionalidad
- **Generic relations**: Relaciones polimórficas
- **Permisos**: Vincular permisos a modelos
- **Introspección**: Obtener información de modelos
- **Auditoría**: Registrar cambios en cualquier modelo

### 🔑 Campos Principales
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `app_label` | String | Nombre de la app (accounts, empresas) |
| `model` | String | Nombre del modelo (User, Empresa) |

### 🎬 Casos de Uso
1. **Permisos**: `Permission` usa ContentType
2. **HistorialCambios**: Registrar cambios en cualquier modelo
3. **Generic FK**: Comentarios, tags, etc
4. **Sistema**: Operaciones internas de Django

---

## 📊 TABLA COMPARATIVA: MODELOS SIMILARES

### Usuarios vs Perfiles de Usuarios

| Característica | User | PerfilUsuario |
|---------------|------|---------------|
| **Propósito** | Autenticación | Datos personales |
| **Obligatorio** | Sí | Sí (creado automáticamente) |
| **Modificable** | Django core | Personalizado |
| **Campos** | Login, password, permisos | Documento, teléfono, profesión |
| **Uso principal** | Seguridad y acceso | Información del usuario |
| **Editable por usuario** | Parcialmente | Totalmente |

### Empresa vs PerfilEmpresa

| Característica | Empresa | PerfilEmpresa |
|---------------|---------|---------------|
| **Propósito** | Datos legales | Datos comerciales |
| **Obligatorio** | Sí | No |
| **Criticidad** | Alta (legal) | Media (marketing) |
| **Campos** | NIT, régimen, tributación | Logo, redes sociales |
| **Uso principal** | Contabilidad | Presentación |
| **Estado** | Implementado | Preparado (futuro) |

### Empresas (modelo) vs Empresas Activas por Usuario

| Característica | Empresa | EmpresaActiva |
|---------------|---------|---------------|
| **Propósito** | Datos de empresa | Asignación usuario-empresa |
| **Tipo** | Modelo maestro | Tabla relación |
| **Contiene** | Info de la empresa | Quién accede |
| **Cantidad** | Una por empresa | Muchas por empresa |
| **Uso principal** | Almacenar datos | Controlar acceso |

---

## 🎯 FLUJO DE TRABAJO TÍPICO

### Registro de Usuario
```
1. User se crea (username, email, password)
   ↓
2. PerfilUsuario se crea automáticamente (señal)
   ↓
3. Usuario completa perfil (documento, teléfono, etc)
   ↓
4. Admin asigna a Grupo (Contador)
   ↓
5. Admin crea EmpresaActiva (vincula usuario-empresa)
   ↓
6. Usuario accede y trabaja en su empresa
```

### Cambio de Empresa Activa
```
1. Usuario tiene múltiples EmpresaActiva
   ↓
2. Selecciona cambiar empresa
   ↓
3. Sistema actualiza empresa_activa_en_sesion
   ↓
4. Todas las operaciones usan nueva empresa
   ↓
5. HistorialCambios registra el cambio
```

---

## 📚 REFERENCIAS Y MEJORES PRÁCTICAS

### Cuándo usar cada modelo

**User**:
- ✅ Login/logout
- ✅ Verificar permisos
- ✅ Auditoría de acciones
- ❌ Almacenar datos personales (usar PerfilUsuario)

**PerfilUsuario**:
- ✅ Formularios de registro
- ✅ Perfiles de usuario
- ✅ Datos de contacto
- ❌ Autenticación (usar User)

**Empresa**:
- ✅ Configuración contable
- ✅ Datos tributarios
- ✅ Información legal
- ❌ Marketing/redes sociales (usar PerfilEmpresa futuro)

**EmpresaActiva**:
- ✅ Asignar usuarios a empresas
- ✅ Controlar acceso
- ✅ Cambiar empresa en sesión
- ❌ Almacenar datos de empresa (usar Empresa)

**Catálogos (Tercero, Impuesto, etc)**:
- ✅ Datos de referencia
- ✅ Listados para selección
- ✅ Configuración del sistema
- ❌ Transacciones (usar modelos específicos)

---

## 🔚 CONCLUSIÓN

El Panel Desarrollador de S_CONTABLE está **meticulosamente organizado** en secciones lógicas:

1. **Gestión de Usuarios**: Control total de acceso y permisos
2. **Empresas**: Gestión multi-empresa con auditoría completa
3. **Catálogos**: Tablas maestras para el sistema contable
4. **Sistema**: Modelos internos de Django

Cada modelo tiene un **propósito específico** y trabajan en conjunto para proporcionar un sistema contable completo, seguro y auditable según las normativas colombianas.

---

**Fecha de creación**: 2025-11-10  
**Versión**: 1.0  
**Sistema**: S_CONTABLE - Sistema Contable Colombiano  
**Framework**: Django 5.2.7
