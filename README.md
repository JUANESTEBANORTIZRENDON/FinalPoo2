# � S_CONTABLE - Comandos Esenciales

## ⚡ Comandos Rápidos

### 1️⃣ Activar Entorno Virtual
```bash
.\env\Scripts\Activate.ps1
```

### 2️⃣ Instalar Dependencias (primera vez)
```bash
pip install -r requirements.txt
```

### 3️⃣ Aplicar Migraciones
```bash
python manage.py migrate
```

### 4️⃣ Crear Superusuario (primera vez)
```bash
python manage.py createsuperuser
```
**Datos por defecto:**
- Usuario: `admin`
- Email: `admin@scontable.com`
- Contraseña: `Admin123!`

### 5️⃣ Ejecutar Servidor
```bash
python manage.py runserver
```
Acceder en: http://127.0.0.1:8000/

---

## � Flujo de Trabajo Diario

```bash
# 1. Activar entorno
.\env\Scripts\Activate.ps1

# 2. Ejecutar servidor
python manage.py runserver
```

---

## 🛠️ Comandos de Desarrollo

### Cuando cambias modelos
```bash
python manage.py makemigrations
python manage.py migrate
```

### Verificar proyecto
```bash
python manage.py check
```

### Acceder al admin
- URL: http://127.0.0.1:8000/admin/
- Usuario: `admin`
- Contraseña: `Admin123!`

---

## 📌 URLs Importantes

- **Admin**: http://127.0.0.1:8000/admin/
- **Login**: http://127.0.0.1:8000/accounts/login/
- **Dashboard**: http://127.0.0.1:8000/accounts/dashboard/

---

## ⚠️ Importante

- **Siempre activar el entorno virtual primero**
- **No subir el archivo `.env` al repositorio**
- **Hacer migraciones después de cambiar modelos**

