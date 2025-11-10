"""
Script de prueba para verificar que SendGrid está configurado correctamente.
"""
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Configurar variables de entorno (obtener de .env o variables de sistema)
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
FROM_EMAIL = os.getenv("EMAIL_HOST_USER", "juanestebanortizrendon24072004@gmail.com")
TO_EMAIL = FROM_EMAIL

print("=" * 70)
print("PRUEBA DE SENDGRID")
print("=" * 70)
print(f"\n📧 From: {FROM_EMAIL}")
print(f"📧 To: {TO_EMAIL}")
print(f"🔑 API Key: {SENDGRID_API_KEY[:20]}...")

try:
    # Crear el mensaje
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=TO_EMAIL,
        subject='✅ Prueba de SendGrid - S_CONTABLE',
        html_content='''
        <h2>🎉 ¡SendGrid Configurado Exitosamente!</h2>
        <p>Este email confirma que SendGrid está funcionando correctamente en tu aplicación S_CONTABLE.</p>
        <h3>✅ Detalles de la Prueba:</h3>
        <ul>
            <li>Servicio: SendGrid API</li>
            <li>Aplicación: S_CONTABLE Django</li>
            <li>Estado: Funcionando</li>
        </ul>
        <p><strong>Ya puedes enviar emails de activación y recuperación de contraseña.</strong></p>
        <hr>
        <p><em>Enviado desde S_CONTABLE - Sistema Contable Colombiano</em></p>
        '''
    )
    
    # Enviar el email
    print("\n📤 Enviando email de prueba...")
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    response = sg.send(message)
    
    # Verificar respuesta
    print(f"\n✅ Email enviado exitosamente!")
    print(f"📊 Status Code: {response.status_code}")
    print(f"📊 Headers: {response.headers}")
    
    if response.status_code == 202:
        print("\n🎉 ¡ÉXITO! SendGrid aceptó el email.")
        print(f"📬 Revisa tu bandeja: {TO_EMAIL}")
        print("⏰ El email debería llegar en menos de 1 minuto.")
    else:
        print(f"\n⚠️ Status code inesperado: {response.status_code}")
        
except Exception as e:
    print(f"\n❌ Error al enviar email:")
    print(f"   Tipo: {type(e).__name__}")
    print(f"   Mensaje: {str(e)}")
    
    if "forbidden" in str(e).lower():
        print("\n⚠️ PROBLEMA: El sender no está verificado en SendGrid")
        print("   SOLUCIÓN:")
        print("   1. Ve a: https://app.sendgrid.com/settings/sender_auth")
        print("   2. Verifica el email: estebanortizrendon2004@gmail.com")
        print("   3. Revisa tu bandeja y confirma la verificación")
    elif "unauthorized" in str(e).lower():
        print("\n⚠️ PROBLEMA: API Key inválida o sin permisos")
        print("   SOLUCIÓN:")
        print("   1. Ve a: https://app.sendgrid.com/settings/api_keys")
        print("   2. Verifica que la API Key tenga 'Full Access'")
        print("   3. Genera una nueva si es necesario")

print("\n" + "=" * 70)
