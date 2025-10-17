# 🔐 S_CONTABLE - DOCUMENTACIÓN DE PRUEBAS JWT

## 🎯 **GUÍA PASO A PASO PARA VALIDAR TOKENS JWT**

Esta documentación te guía para probar el sistema JWT completo: desde crear un usuario en la interfaz web hasta validar tokens en terminal y verificar que cambien al modificar la contraseña.

---

## 🚀 **PREPARACIÓN DEL ENTORNO**

### **1️⃣ INICIAR EL PROYECTO**

```powershell
# 1. Navegar al directorio del proyecto
cd C:\Users\ASUS\S_CONTABLE

# 2. Activar entorno virtual
.\env\Scripts\Activate.ps1

# 3. Verificar configuración
python manage.py check

# 4. Aplicar migraciones si es necesario
python manage.py migrate

# 5. Ejecutar servidor de desarrollo
python manage.py runserver
```

**✅ Resultado esperado:** 
- Servidor ejecutándose en: http://127.0.0.1:8000
- Sin errores en consola
- Mensaje: "Starting development server at http://127.0.0.1:8000/"

---

## 👤 **CREAR USUARIO EN LA INTERFAZ WEB**

### **2️⃣ REGISTRO DE USUARIO**

1. **Abrir navegador** y ir a: http://127.0.0.1:8000/accounts/register/

2. **Llenar formulario completo** con estos datos de ejemplo:
   ```
   Username: jwt_test_user
   Email: tu-email-real@gmail.com  (usa tu email real)
   Contraseña: TestPassword123!
   Confirmar contraseña: TestPassword123!
   Nombres: JWT
   Apellidos: Test User
   Tipo de documento: Cédula de Ciudadanía
   Número de documento: 1234567890
   Teléfono: 3001234567
   ✅ Acepto los Términos y Condiciones
   ✅ Acepto la Política de Privacidad
   ```

3. **Hacer clic en "Registrar"**

**✅ Resultado esperado:**
- Redirección a página de confirmación
- Mensaje: "Se ha enviado un email de activación"
- Email recibido en tu bandeja de entrada

### **3️⃣ ACTIVACIÓN DE CUENTA**

**🔔 IMPORTANTE:** En lugar de hacer clic en el enlace del email, vamos a activar manualmente para poder controlar el proceso de prueba.

#### **Opción A: Activación Manual (Recomendada para pruebas)**

```powershell
# Abrir shell de Django (en nueva terminal)
cd C:\Users\ASUS\S_CONTABLE
.\env\Scripts\Activate.ps1
python manage.py shell
```

```python
# Dentro del shell de Django, ejecutar:
from django.contrib.auth.models import User

# Buscar el usuario creado
user = User.objects.get(username='jwt_test_user')
print(f"Usuario encontrado: {user.username}")
print(f"Email: {user.email}")
print(f"Activo: {user.is_active}")

# Activar el usuario
user.is_active = True
user.save()
print("✅ Usuario activado exitosamente")

# Salir del shell
exit()
```

#### **Opción B: Activación por Email (Proceso real)**

1. **Revisar tu email** (bandeja de entrada o spam)
2. **Hacer clic en el enlace** de activación
3. **Verificar** que aparezca mensaje de "Cuenta activada"

---

## 🔐 **VALIDACIÓN DE JWT EN TERMINAL**

### **4️⃣ OBTENER TOKEN JWT INICIAL**

```powershell
# Preparar datos de login en formato JSON
$loginData = @{
    username = "jwt_test_user"
    password = "TestPassword123!"
} | ConvertTo-Json

# Realizar petición de login a la API
$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/token/" -Method POST -Body $loginData -ContentType "application/json"

# Extraer tokens
$accessToken1 = $response.access
$refreshToken1 = $response.refresh

# Mostrar tokens obtenidos
Write-Host "🎫 ACCESS TOKEN INICIAL:"
Write-Host $accessToken1
Write-Host ""
Write-Host "🔄 REFRESH TOKEN INICIAL:"
Write-Host $refreshToken1
```

**✅ Resultado esperado:**
```
🎫 ACCESS TOKEN INICIAL:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYwNjgwNzQ1...

🔄 REFRESH TOKEN INICIAL:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2MDc2NjI0NQ...
```

### **5️⃣ VALIDAR TOKEN CON API**

```powershell
# Crear headers de autorización
$headers = @{
    "Authorization" = "Bearer $accessToken1"
    "Content-Type" = "application/json"
}

# Probar endpoint protegido
$userInfo = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/me/" -Method GET -Headers $headers

# Mostrar información del usuario
Write-Host "👤 INFORMACIÓN DEL USUARIO AUTENTICADO:"
$userInfo | ConvertTo-Json -Depth 3
```

**✅ Resultado esperado:**
```json
{
  "username": "jwt_test_user",
  "email": "tu-email@gmail.com",
  "first_name": "JWT",
  "last_name": "Test User",
  "is_active": true,
  "date_joined": "2025-10-17T05:30:00Z"
}
```

### **6️⃣ DECODIFICAR TOKEN PARA VER CONTENIDO**

```powershell
# Guardar token en variable para análisis
$tokenParts = $accessToken1.Split('.')
$payload = $tokenParts[1]

# Agregar padding si es necesario
while ($payload.Length % 4 -ne 0) {
    $payload += "="
}

# Decodificar base64
$decodedBytes = [System.Convert]::FromBase64String($payload)
$decodedText = [System.Text.Encoding]::UTF8.GetString($decodedBytes)
$tokenData = $decodedText | ConvertFrom-Json

Write-Host "📋 CONTENIDO DEL TOKEN:"
Write-Host "User ID: $($tokenData.user_id)"
Write-Host "Token Type: $($tokenData.token_type)"
Write-Host "JTI (JWT ID): $($tokenData.jti)"
Write-Host "Expira: $(Get-Date -UnixTimeSeconds $tokenData.exp)"
Write-Host "Emitido: $(Get-Date -UnixTimeSeconds $tokenData.iat)"
```

**✅ Resultado esperado:**
```
📋 CONTENIDO DEL TOKEN:
User ID: 15
Token Type: access
JTI (JWT ID): 3f7038ba6dd048ad8db3e6d16d8ee8f9
Expira: 17/10/2025 01:00:00
Emitido: 17/10/2025 00:45:00
```

---

## 🔄 **CAMBIO DE CONTRASEÑA Y VALIDACIÓN**

### **7️⃣ CAMBIAR CONTRASEÑA EN LA INTERFAZ WEB**

1. **Ir a reset de contraseña**: http://127.0.0.1:8000/accounts/password_reset/

2. **Ingresar email**: `tu-email-real@gmail.com` (el mismo del registro)

3. **Hacer clic en "Enviar Enlace"**

4. **Verificar página de confirmación**: "📧 Email Enviado Exitosamente"

5. **Revisar email** (puede tardar unos minutos)

6. **Hacer clic en enlace** del email de reset

7. **Ingresar nueva contraseña**:
   ```
   Nueva contraseña: NewPassword456!
   Confirmar contraseña: NewPassword456!
   ```

8. **Hacer clic en "Cambiar Contraseña"**

**✅ Resultado esperado:**
- Mensaje de "Contraseña cambiada exitosamente"
- Redirección automática al login

### **8️⃣ OBTENER NUEVO TOKEN JWT**

```powershell
# Preparar datos con NUEVA contraseña
$newLoginData = @{
    username = "jwt_test_user"
    password = "NewPassword456!"  # ← Nueva contraseña
} | ConvertTo-Json

# Obtener nuevos tokens
$newResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/token/" -Method POST -Body $newLoginData -ContentType "application/json"

# Extraer nuevos tokens
$accessToken2 = $newResponse.access
$refreshToken2 = $newResponse.refresh

Write-Host "🎫 NUEVO ACCESS TOKEN:"
Write-Host $accessToken2
Write-Host ""
Write-Host "🔄 NUEVO REFRESH TOKEN:"
Write-Host $refreshToken2
```

### **9️⃣ COMPARAR TOKENS ANTES Y DESPUÉS**

```powershell
Write-Host "🔍 COMPARACIÓN DE TOKENS:"
Write-Host "=================================="
Write-Host ""
Write-Host "Token ORIGINAL (contraseña anterior):"
Write-Host $accessToken1.Substring(0, 50) + "..."
Write-Host ""
Write-Host "Token NUEVO (contraseña nueva):"
Write-Host $accessToken2.Substring(0, 50) + "..."
Write-Host ""

# Verificar que son diferentes
if ($accessToken1 -eq $accessToken2) {
    Write-Host "❌ ERROR: Los tokens son IGUALES"
    Write-Host "   Esto indica un problema en el sistema JWT"
} else {
    Write-Host "✅ ÉXITO: Los tokens son DIFERENTES"
    Write-Host "   El sistema JWT funciona correctamente"
}
```

### **🔟 DECODIFICAR NUEVO TOKEN**

```powershell
# Decodificar nuevo token
$newTokenParts = $accessToken2.Split('.')
$newPayload = $newTokenParts[1]

while ($newPayload.Length % 4 -ne 0) {
    $newPayload += "="
}

$newDecodedBytes = [System.Convert]::FromBase64String($newPayload)
$newDecodedText = [System.Text.Encoding]::UTF8.GetString($newDecodedBytes)
$newTokenData = $newDecodedText | ConvertFrom-Json

Write-Host "📋 COMPARACIÓN DE CONTENIDO:"
Write-Host "=============================="
Write-Host "JTI Original: $($tokenData.jti)"
Write-Host "JTI Nuevo:    $($newTokenData.jti)"
Write-Host ""
Write-Host "Emitido Original: $(Get-Date -UnixTimeSeconds $tokenData.iat)"
Write-Host "Emitido Nuevo:    $(Get-Date -UnixTimeSeconds $newTokenData.iat)"
```

---

## ✅ **VALIDACIÓN FINAL**

### **1️⃣1️⃣ PROBAR QUE EL NUEVO TOKEN FUNCIONA**

```powershell
# Crear headers con nuevo token
$newHeaders = @{
    "Authorization" = "Bearer $accessToken2"
    "Content-Type" = "application/json"
}

# Probar endpoint con nuevo token
$newUserInfo = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/me/" -Method GET -Headers $newHeaders

Write-Host "👤 VALIDACIÓN CON NUEVO TOKEN:"
Write-Host "Usuario: $($newUserInfo.username)"
Write-Host "Email: $($newUserInfo.email)"
Write-Host "✅ El nuevo token funciona correctamente"
```

### **1️⃣2️⃣ PROBAR QUE LA CONTRASEÑA ANTERIOR NO FUNCIONA**

```powershell
# Intentar login con contraseña anterior
$oldPasswordData = @{
    username = "jwt_test_user"
    password = "TestPassword123!"  # ← Contraseña anterior
} | ConvertTo-Json

try {
    $failResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/token/" -Method POST -Body $oldPasswordData -ContentType "application/json"
    Write-Host "❌ ERROR: La contraseña anterior aún funciona"
} catch {
    Write-Host "✅ CORRECTO: La contraseña anterior ya no funciona"
    Write-Host "   Status: $($_.Exception.Response.StatusCode)"
}
```

---

## 🧹 **LIMPIEZA DE DATOS DE PRUEBA**

### **1️⃣3️⃣ ELIMINAR USUARIO DE PRUEBA**

```powershell
# Abrir shell de Django
python manage.py shell
```

```python
# Dentro del shell:
from django.contrib.auth.models import User

# Buscar y eliminar usuario de prueba
try:
    user = User.objects.get(username='jwt_test_user')
    user.delete()
    print("✅ Usuario de prueba eliminado exitosamente")
except User.DoesNotExist:
    print("ℹ️ Usuario de prueba no encontrado")

# Salir del shell
exit()
```

---

## 📊 **RESULTADOS ESPERADOS**

### **✅ VALIDACIÓN EXITOSA:**

Si todo funciona correctamente, deberías ver:

1. **✅ Usuario registrado** en la interfaz web
2. **✅ Email de activación** recibido
3. **✅ Token JWT obtenido** después del login
4. **✅ API responde** con información del usuario
5. **✅ Contraseña cambiada** vía web
6. **✅ Nuevo token diferente** al anterior
7. **✅ Contraseña anterior** ya no funciona
8. **✅ Nuevo token funciona** correctamente

### **🔍 INDICADORES DE ÉXITO:**

#### **Tokens Diferentes:**
```
Token Original: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoi...
Token Nuevo:    eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoi...
                ↑ Diferentes JTI y timestamps
```

#### **JTI Únicos:**
```
JTI Original: 3f7038ba6dd048ad8db3e6d16d8ee8f9
JTI Nuevo:    0ca90eb287294e4ca866147797776b550
              ↑ Completamente diferentes
```

#### **Timestamps Diferentes:**
```
Emitido Original: 17/10/2025 00:45:00
Emitido Nuevo:    17/10/2025 01:15:00
                  ↑ Nuevo es más reciente
```

---

## 🚨 **SOLUCIÓN DE PROBLEMAS**

### **❌ Error: "Invalid credentials"**
**Causa:** Usuario no activado o contraseña incorrecta
**Solución:** Verificar activación manual o revisar contraseña

### **❌ Error: "Token has expired"**
**Causa:** Token JWT expiró (15 minutos)
**Solución:** Obtener nuevo token con login

### **❌ Error: "User not found"**
**Causa:** Usuario no existe en base de datos
**Solución:** Verificar registro en interfaz web

### **❌ Error: "CSRF verification failed"**
**Causa:** Problema de configuración
**Solución:** Verificar CSRF_TRUSTED_ORIGINS en .env

### **❌ Los tokens son iguales**
**Causa:** Problema en configuración JWT
**Solución:** Verificar SECRET_KEY y configuración SimpleJWT

---

## 🎯 **COMANDOS RÁPIDOS DE REFERENCIA**

### **Login y Token:**
```powershell
$loginData = @{username="usuario"; password="contraseña"} | ConvertTo-Json
$tokens = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/token/" -Method POST -Body $loginData -ContentType "application/json"
```

### **Probar API:**
```powershell
$headers = @{"Authorization" = "Bearer $($tokens.access)"}
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/me/" -Headers $headers
```

### **Activar Usuario:**
```python
from django.contrib.auth.models import User
User.objects.filter(username='usuario').update(is_active=True)
```

---

## 🎉 **CONCLUSIÓN**

Esta prueba valida que:

1. **🔐 Sistema JWT funciona** correctamente
2. **🔄 Tokens cambian** al cambiar contraseña
3. **🛡️ Seguridad implementada** adecuadamente
4. **🌐 API REST operativa** y segura
5. **👤 Sistema de usuarios** completo y funcional

**Si todos los pasos se completan exitosamente, tu sistema S_CONTABLE está listo para producción con autenticación JWT segura.**
