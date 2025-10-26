#!/usr/bin/env python
"""
Script para generar una SECRET_KEY segura para Django.
Ejecuta este script y copia la clave generada a las variables de entorno de Render.
"""
import secrets
import string

def get_random_secret_key():
    """Genera una clave secreta aleatoria de 50 caracteres"""
    chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(chars) for _ in range(50))

if __name__ == '__main__':
    secret_key = get_random_secret_key()
    print("=" * 80)
    print("🔐 SECRET_KEY GENERADA PARA DJANGO")
    print("=" * 80)
    print("\n✅ Copia esta clave y configúrala en Render:\n")
    print(f"SECRET_KEY={secret_key}")
    print("\n" + "=" * 80)
    print("📋 INSTRUCCIONES PARA RENDER:")
    print("=" * 80)
    print("1. Ve a tu proyecto en Render Dashboard")
    print("2. Click en 'Environment' en el menú lateral")
    print("3. Click en 'Add Environment Variable'")
    print("4. Key: SECRET_KEY")
    print("5. Value: (pega la clave generada arriba)")
    print("6. Click en 'Save Changes'")
    print("7. Render re-desplegará automáticamente tu aplicación")
    print("=" * 80)
