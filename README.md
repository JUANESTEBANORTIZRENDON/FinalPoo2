# S_CONTABLE - Sistema de Gestión Contable

## Módulos Implementados

| Módulo            | Estado      | Descripción                                  |
| ----------------- | ----------- | -------------------------------------------- |
| **Autenticación** | Completado  | Login, registro y gestión de usuarios        |
| **Empresas**      | Completado  | Gestión de múltiples empresas                |
| **Catálogos**     | Completado  | Métodos de pago, tipos de documento, etc.    |
| **Tesoreria**     | Completado  | Gestión de cobros, pagos y cuentas bancarias |
| **Facturación**   | En Progreso | Facturas, notas crédito/débito               |
| **Contabilidad**  | Pendiente   | Asientos contables, mayor general            |
| **Reportes**      | Parcial     | Reportes financieros básicos                 |

## Vista Rápida de Tesorería

### Características Implementadas:

- Gestión de cuentas bancarias
- Registro de cobros y pagos
- Conciliación bancaria
- Reportes de flujo de caja
- Control de saldos por cuenta

### Acceso Rápido:

- **Cuentas Bancarias**: `/tesoreria/cuentas/`
- **Cobros**: `/tesoreria/cobros/`
- **Pagos**: `/tesoreria/pagos/`
- **Reportes**: `/tesoreria/reportes/`

## Comandos Rápidos

### 1️⃣ Habilitar Scripts en PowerShell### 1️⃣ Activar Entorno Virtual

```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\env\Scripts\Activate.ps1
```

`bash`bash

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser.\env\Scripts\Activate.ps1

````

*Solo necesario la primera vez si da error de permisos*

### 2️⃣ Instalar Dependencias (primera vez)

### 2️⃣ Crear Entorno Virtual (si no existe)```bash

```bashpip install -r requirements.txt

python -m venv env```

```

### 3️⃣ Aplicar Migraciones

### 3️⃣ Activar Entorno Virtual```bash

```bashpython manage.py migrate

.\env\Scripts\Activate.ps1```

```

### 4️⃣ Crear Superusuario (primera vez)

### 4️⃣ Instalar Dependencias```bash

```bashpython manage.py createsuperuser

pip install -r requirements.txt```

```**Datos por defecto:**

- Usuario: `admin`

### 5️⃣ Aplicar Migraciones- Email: `admin@scontable.com`

```bash- Contraseña: `Admin123!`

python manage.py migrate

```### 5️⃣ Ejecutar Servidor

```bash

### 6️⃣ Crear Superusuariopython manage.py runserver

```bash```

python manage.py createsuperuserAcceder en: http://127.0.0.1:8000/

```

**Datos por defecto:**---

- Usuario: `admin`

- Email: `admin@scontable.com`## � Flujo de Trabajo Diario

- Contraseña: `Admin123!`

```bash

---# 1. Activar entorno

.\env\Scripts\Activate.ps1

## ⚡ Uso Diario

# 2. Ejecutar servidor

```bashpython manage.py runserver

# 1. Activar entorno virtual```

.\env\Scripts\Activate.ps1

---

# 2. Ejecutar servidor

python manage.py runserver## 🛠️ Comandos de Desarrollo

```

### Cuando cambias modelos

Acceder en: **http://127.0.0.1:8000/**```bash

python manage.py makemigrations

---python manage.py migrate

```

## 🛠️ Comandos de Desarrollo

### Verificar proyecto

### Cuando cambias modelos```bash

```bashpython manage.py check

python manage.py makemigrations```

python manage.py migrate

```### Acceder al admin

- URL: http://127.0.0.1:8000/admin/

### Verificar proyecto- Usuario: `admin`

```bash- Contraseña: `Admin123!`

python manage.py check

```---



### Acceder al admin## 📌 URLs Importantes

- **URL**: http://127.0.0.1:8000/admin/

- **Usuario**: `admin`- **Admin**: http://127.0.0.1:8000/admin/

- **Contraseña**: `Admin123!`- **Login**: http://127.0.0.1:8000/accounts/login/

- **Dashboard**: http://127.0.0.1:8000/accounts/dashboard/

---

---

## 📌 URLs Importantes

## ⚠️ Importante

- **Admin**: http://127.0.0.1:8000/admin/

- **Login**: http://127.0.0.1:8000/accounts/login/- **Siempre activar el entorno virtual primero**

- **Dashboard**: http://127.0.0.1:8000/accounts/dashboard/- **No subir el archivo `.env` al repositorio**

- **Hacer migraciones después de cambiar modelos**

---


## ⚠️ Solución de Problemas

### Error: "Activate.ps1 is not recognized"
```bash
# Solución: Habilitar ejecución de scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error: "No existe el entorno virtual"
```bash
# Solución: Crear el entorno virtual
python -m venv env
```

### Error: "password authentication failed" (Base de datos)
El proyecto está configurado para PostgreSQL en la nube. Para trabajar localmente:

**Opción 1: Usar SQLite (Recomendado para desarrollo local)**
1. Abrir `core/settings.py`
2. Comentar la configuración de PostgreSQL
3. Descomentar la configuración de SQLite:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Opción 2: Usar tus credenciales de PostgreSQL**
1. Edita el archivo `.env` con tus credenciales
2. Ejecuta las migraciones

### Reinstalar dependencias
```bash
pip install --force-reinstall -r requirements.txt
```

---

## 📝 Notas Importantes

- ✅ **Siempre activar el entorno virtual primero**
- ✅ **No subir el archivo `.env` al repositorio**
- ✅ **Hacer migraciones después de cambiar modelos**
- ✅ **El entorno virtual está en la carpeta `env/` (ignorada por git)**
````
