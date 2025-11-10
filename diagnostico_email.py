"""
Script de diagnóstico para verificar configuración de email en Render.
Ejecutar en el shell de Render para ver exactamente qué está pasando.
"""
import os
import socket

# Constante para valores no configurados
NOT_CONFIGURED = 'NO CONFIGURADA'

print("=" * 60)
print("DIAGNÓSTICO DE CONFIGURACIÓN DE EMAIL")
print("=" * 60)

# 1. Verificar variables de entorno
print("\n1️⃣ VARIABLES DE ENTORNO:")
print("-" * 60)
email_vars = {
    'EMAIL_BACKEND': os.getenv('EMAIL_BACKEND', NOT_CONFIGURED),
    'EMAIL_HOST': os.getenv('EMAIL_HOST', NOT_CONFIGURED),
    'EMAIL_PORT': os.getenv('EMAIL_PORT', NOT_CONFIGURED),
    'EMAIL_USE_SSL': os.getenv('EMAIL_USE_SSL', NOT_CONFIGURED),
    'EMAIL_USE_TLS': os.getenv('EMAIL_USE_TLS', NOT_CONFIGURED),
    'EMAIL_HOST_USER': os.getenv('EMAIL_HOST_USER', NOT_CONFIGURED),
    'EMAIL_HOST_PASSWORD': '***' if os.getenv('EMAIL_HOST_PASSWORD') else NOT_CONFIGURED,
}

for key, value in email_vars.items():
    status = "✅" if value not in [NOT_CONFIGURED, None, ''] else "❌"
    print(f"{status} {key}: {value}")

# 2. Verificar tipos después de conversión
print("\n2️⃣ TIPOS DE DATOS (después de conversión):")
print("-" * 60)
try:
    port = int(os.getenv("EMAIL_PORT", "465"))
    print(f"✅ EMAIL_PORT: {port} (tipo: {type(port).__name__})")
except Exception as e:
    print(f"❌ EMAIL_PORT: Error - {e}")

try:
    use_ssl = os.getenv("EMAIL_USE_SSL", "True").lower() in ('true', '1', 'yes')
    print(f"✅ EMAIL_USE_SSL: {use_ssl} (tipo: {type(use_ssl).__name__})")
except Exception as e:
    print(f"❌ EMAIL_USE_SSL: Error - {e}")

# 3. Verificar conectividad de red
print("\n3️⃣ CONECTIVIDAD DE RED:")
print("-" * 60)
try:
    host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    port = int(os.getenv('EMAIL_PORT', '465'))
    print(f"Intentando conectar a {host}:{port}...")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    result = sock.connect_ex((host, port))
    sock.close()
    
    if result == 0:
        print(f"✅ Puerto {port} está ABIERTO y accesible")
    else:
        print(f"❌ Puerto {port} está CERRADO o BLOQUEADO (código: {result})")
except Exception as e:
    print(f"❌ Error de conectividad: {e}")

# 4. Probar autenticación SMTP
print("\n4️⃣ PRUEBA DE AUTENTICACIÓN SMTP:")
print("-" * 60)
try:
    import smtplib
    from email.mime.text import MIMEText
    
    host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    port = int(os.getenv('EMAIL_PORT', '465'))
    user = os.getenv('EMAIL_HOST_USER')
    password = os.getenv('EMAIL_HOST_PASSWORD')
    
    if not user or not password:
        print("❌ Falta EMAIL_HOST_USER o EMAIL_HOST_PASSWORD")
    else:
        print(f"Conectando a {host}:{port} con usuario: {user}...")
        
        # Usar SSL (puerto 465)
        with smtplib.SMTP_SSL(host, port, timeout=30) as server:
            print("✅ Conexión SSL establecida")
            server.login(user, password)
            print("✅ Autenticación EXITOSA")
            
            # Enviar email de prueba
            msg = MIMEText("Este es un email de prueba desde Render")
            msg['Subject'] = 'Prueba de Configuración SMTP'
            msg['From'] = user
            msg['To'] = user
            
            server.send_message(msg)
            print(f"✅ Email de prueba enviado a {user}")
            
except Exception as e:
    print(f"❌ Error en autenticación SMTP: {type(e).__name__}: {e}")

# 5. Verificar configuración de Django
print("\n5️⃣ CONFIGURACIÓN DE DJANGO:")
print("-" * 60)
try:
    from django.conf import settings
    
    django_email_config = {
        'EMAIL_BACKEND': settings.EMAIL_BACKEND,
        'EMAIL_HOST': settings.EMAIL_HOST,
        'EMAIL_PORT': f"{settings.EMAIL_PORT} (tipo: {type(settings.EMAIL_PORT).__name__})",
        'EMAIL_USE_SSL': f"{settings.EMAIL_USE_SSL} (tipo: {type(settings.EMAIL_USE_SSL).__name__})",
        'EMAIL_USE_TLS': f"{settings.EMAIL_USE_TLS} (tipo: {type(settings.EMAIL_USE_TLS).__name__})",
        'EMAIL_TIMEOUT': settings.EMAIL_TIMEOUT,
        'EMAIL_HOST_USER': settings.EMAIL_HOST_USER or NOT_CONFIGURED,
        'EMAIL_HOST_PASSWORD': '***' if settings.EMAIL_HOST_PASSWORD else NOT_CONFIGURED,
    }
    
    for key, value in django_email_config.items():
        print(f"  {key}: {value}")
        
except Exception as e:
    print(f"❌ Error al leer configuración de Django: {e}")

# 6. Resumen
print("\n" + "=" * 60)
print("RESUMEN Y RECOMENDACIONES")
print("=" * 60)

issues = []
if os.getenv('EMAIL_PORT', '465') != '465':
    issues.append("❌ EMAIL_PORT debe ser 465")
if os.getenv('EMAIL_USE_SSL', 'True').lower() not in ('true', '1', 'yes'):
    issues.append("❌ EMAIL_USE_SSL debe ser 'True'")
if not os.getenv('EMAIL_HOST_USER'):
    issues.append("❌ EMAIL_HOST_USER no configurado")
if not os.getenv('EMAIL_HOST_PASSWORD'):
    issues.append("❌ EMAIL_HOST_PASSWORD no configurado")

if issues:
    print("\n⚠️ PROBLEMAS DETECTADOS:")
    for issue in issues:
        print(f"  {issue}")
else:
    print("\n✅ Todas las variables están configuradas correctamente")

print("\n📋 CHECKLIST:")
print("  1. EMAIL_PORT = 465")
print("  2. EMAIL_USE_SSL = True")
print("  3. EMAIL_HOST_USER = tu-email@gmail.com")
print("  4. EMAIL_HOST_PASSWORD = app-password-16-chars")
print("  5. Eliminar variable EMAIL_USE_TLS de Render (no es necesaria)")
print("=" * 60)
