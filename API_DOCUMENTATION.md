# 🚀 API REST + JWT - S_CONTABLE

## 🏗️ **Arquitectura de Convivencia**

Este proyecto implementa **convivencia de autenticación**:
- **Vistas MVT (HTML)**: Usan sesiones Django (sin cambios)
- **API REST**: Usa JWT para móviles/SPA

## 📋 **Comandos PowerShell Exactos**

### **Instalación y Configuración**

```powershell
# 1. Activar entorno virtual
cd c:\Users\ASUS\S_CONTABLE
.\env\Scripts\Activate.ps1

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno (editar .env manualmente)
# Copiar .env.example como .env y configurar

# 4. Crear migraciones
python manage.py makemigrations

# 5. Aplicar migraciones
python manage.py migrate

# 6. Crear superusuario
python manage.py createsuperuser

# 7. Ejecutar servidor
python manage.py runserver
```


## 🔐 **Endpoints API**

### **Base URL**: `http://127.0.0.1:8000/api/`

---

### **1. Obtener Tokens JWT**

**POST** `/api/token/`

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "tu_usuario",
    "password": "tu_contraseña"
  }'
```

**Respuesta exitosa:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "tu_usuario",
    "email": "tu@email.com",
    "full_name": "Tu Nombre"
  }
}
```

---

### **2. Renovar Access Token**

**POST** `/api/token/refresh/`

```bash
curl -X POST http://127.0.0.1:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }'
```

**Respuesta:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

### **3. Información del Usuario**

**GET** `/api/me/`

```bash
curl -X GET http://127.0.0.1:8000/api/me/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

**Respuesta:**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "tu_usuario",
    "email": "tu@email.com",
    "first_name": "Tu",
    "last_name": "Nombre",
    "full_name": "Tu Nombre",
    "is_verified": true,
    "date_joined": "2025-10-16T19:30:00Z",
    "last_login": "2025-10-16T20:15:00Z"
  }
}
```

---

### **4. Registro de Usuario**

**POST** `/api/registro/`

```bash
curl -X POST http://127.0.0.1:8000/api/registro/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "nuevo_usuario",
    "email": "nuevo@email.com",
    "password1": "MiContraseñaSegura123",
    "password2": "MiContraseñaSegura123",
    "first_name": "Nuevo",
    "last_name": "Usuario"
  }'
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "message": "Usuario creado exitosamente. Revisa tu email para activar la cuenta.",
  "user_id": 2,
  "email": "nuevo@email.com"
}
```

**Respuesta con errores:**
```json
{
  "success": false,
  "errors": {
    "password2": ["Las contraseñas no coinciden."],
    "email": ["Este email ya está registrado."]
  }
}
```

---

### **5. Activar Cuenta**

**POST** `/api/activar/`

```bash
curl -X POST http://127.0.0.1:8000/api/activar/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "tu_token_de_activacion_del_email"
  }'
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "message": "¡Cuenta activada exitosamente!",
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "user": {
    "id": 2,
    "username": "nuevo_usuario",
    "email": "nuevo@email.com"
  }
}
```

---

### **6. Solicitar Reset de Contraseña**

**POST** `/api/password/reset/`

```bash
curl -X POST http://127.0.0.1:8000/api/password/reset/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "tu@email.com"
  }'
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Si el email existe, recibirás instrucciones para restablecer tu contraseña."
}
```

---

### **7. Confirmar Reset de Contraseña**

**POST** `/api/password/reset/confirm/`

```bash
curl -X POST http://127.0.0.1:8000/api/password/reset/confirm/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "token_del_email",
    "uid": "uid_del_email",
    "password1": "MiNuevaContraseña123",
    "password2": "MiNuevaContraseña123"
  }'
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "message": "Contraseña restablecida exitosamente."
}
```

---

### **8. Logout (Invalidar Refresh Token)**

**POST** `/api/logout/`

```bash
curl -X POST http://127.0.0.1:8000/api/logout/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }'
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Logout exitoso."
}
```

## 🔒 **Configuración de Seguridad**

### **Tokens JWT**
- **Access Token**: 15 minutos (seguridad)
- **Refresh Token**: 1 día (usabilidad)
- **Rotación**: Los refresh tokens se rotan automáticamente
- **Blacklist**: Tokens invalidados se almacenan en blacklist

### **Email Gmail**
- Usa **contraseña de aplicación**, NO tu contraseña normal
- Requiere **verificación en 2 pasos** habilitada
- **NUNCA** subir `GOOGLE_APP_PASSWORD` al repositorio

### **Base de Datos Neon**
- Conexión con **SSL requerido**
- **Connection pooling** habilitado
- **Health checks** automáticos

## 🚨 **Notas de Seguridad**

### **Desarrollo**
- ✅ DEBUG=True (solo desarrollo)
- ✅ HTTP permitido (solo desarrollo)
- ✅ CORS configurado para localhost

### **Producción**
```python
# Activar en producción:
DEBUG = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
```

### **Mejores Prácticas JWT**
- 🔐 **Access tokens cortos** (10-30 min)
- 🔄 **Refresh tokens medianos** (1-7 días)
- 🚫 **Evitar localStorage** para tokens sensibles
- ✅ **Usar httpOnly cookies** o memoria cuando sea posible
- 🗑️ **Blacklist** para logout seguro

## 🔄 **Convivencia MVT + API**

### **Vistas MVT (HTML)**
```python
# Siguen funcionando igual - usan sesiones
def mi_vista_html(request):
    if request.user.is_authenticated:  # ✅ Funciona
        return render(request, 'template.html')
```

### **Vistas API (JWT)**
```python
# Nuevas vistas - usan JWT
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mi_vista_api(request):
    if request.user.is_authenticated:  # ✅ Funciona igual
        return Response({'user': request.user.username})
```

### **Rutas**
- **MVT**: `/accounts/login/`, `/accounts/dashboard/`
- **API**: `/api/token/`, `/api/me/`

## 📱 **Uso en Aplicaciones**

### **Web (HTML/JavaScript)**
```javascript
// Obtener token
const response = await fetch('/api/token/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'user', password: 'pass'})
});
const data = await response.json();

// Usar token
const userResponse = await fetch('/api/me/', {
  headers: {'Authorization': `Bearer ${data.access}`}
});
```

### **React/Vue/Angular**
```javascript
// Configurar interceptor para tokens
axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
```

### **Móvil (React Native/Flutter)**
```javascript
// Almacenar tokens de forma segura
import AsyncStorage from '@react-native-async-storage/async-storage';

await AsyncStorage.setItem('access_token', data.access);
await AsyncStorage.setItem('refresh_token', data.refresh);
```

## 🧪 **Testing**

### **Probar Endpoints**
```bash
# Instalar herramientas de testing
pip install httpie

# Obtener token
http POST :8000/api/token/ username=admin password=admin

# Usar token
http GET :8000/api/me/ "Authorization:Bearer TOKEN_AQUI"
```

### **Browsable API**
Visita: `http://127.0.0.1:8000/api/` para interfaz web de pruebas

## 📞 **Soporte**

Si encuentras problemas:
1. Verifica que todas las dependencias estén instaladas
2. Confirma que las variables de entorno estén configuradas
3. Revisa los logs del servidor Django
4. Verifica que la contraseña de aplicación Gmail sea correcta
