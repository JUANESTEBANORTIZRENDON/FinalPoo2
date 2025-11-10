"""
Script para probar el envío de emails usando la configuración de Django.
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("=" * 70)
print("PRUEBA DE EMAIL CON DJANGO + SENDGRID")
print("=" * 70)

# Mostrar configuración actual
print(f"\n📧 Configuración de Email:")
print(f"  Backend: {settings.EMAIL_BACKEND}")
print(f"  Host User: {settings.EMAIL_HOST_USER}")
print(f"  Default From: {settings.DEFAULT_FROM_EMAIL}")

if hasattr(settings, 'SENDGRID_API_KEY') and settings.SENDGRID_API_KEY:
    print(f"  SendGrid API Key: {settings.SENDGRID_API_KEY[:20]}...")
    print(f"  🎯 Modo: SENDGRID (Producción)")
else:
    print(f"  Email Host: {settings.EMAIL_HOST}")
    print(f"  Email Port: {settings.EMAIL_PORT}")
    print(f"  🎯 Modo: GMAIL SMTP (Desarrollo)")

print("\n" + "-" * 70)

try:
    # Enviar email de prueba
    print("\n📤 Enviando email de prueba...")
    
    subject = "✅ Prueba de Email - S_CONTABLE Django"
    message = """
¡Hola!

Este es un email de prueba desde S_CONTABLE usando Django.

✅ Detalles:
- Sistema: S_CONTABLE
- Framework: Django 5.2.7
- Email Service: SendGrid
- Estado: Funcionando correctamente

Si recibes este email, significa que el sistema de envío de emails 
está configurado correctamente y listo para:

1. Activación de cuentas nuevas
2. Recuperación de contraseñas
3. Notificaciones del sistema

¡Todo está listo para producción! 🚀

---
S_CONTABLE - Sistema Contable Colombiano
    """
    
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = settings.EMAIL_HOST_USER
    
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=[to_email],
        fail_silently=False,
    )
    
    print(f"✅ Email enviado exitosamente!")
    print(f"📬 Destinatario: {to_email}")
    print(f"📨 Remitente: {from_email}")
    print(f"\n🎉 ¡ÉXITO! El sistema de emails está funcionando correctamente.")
    print(f"⏰ Revisa tu bandeja de entrada en: {to_email}")
    
except Exception as e:
    print(f"\n❌ Error al enviar email:")
    print(f"   Tipo: {type(e).__name__}")
    print(f"   Mensaje: {str(e)}")
    
    if "refused" in str(e).lower():
        print("\n⚠️ PROBLEMA: Conexión rechazada")
        print("   CAUSA: Puede ser que Gmail SMTP esté bloqueado")
        print("   SOLUCIÓN: Usar SendGrid en producción")
    elif "authentication" in str(e).lower():
        print("\n⚠️ PROBLEMA: Error de autenticación")
        print("   SOLUCIÓN: Verifica EMAIL_HOST_USER y EMAIL_HOST_PASSWORD")

print("\n" + "=" * 70)
