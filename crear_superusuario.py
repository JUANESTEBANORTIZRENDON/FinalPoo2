#!/usr/bin/env python
"""
Script para crear superusuario automáticamente
Soluciona el problema de contraseñas en blanco
"""
import os
import sys
import django

def main():
    """Crear superusuario con credenciales predefinidas"""
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()
    
    from django.contrib.auth.models import User
    
    print("🔐 CREANDO SUPERUSUARIO PARA S_CONTABLE")
    print("=" * 50)
    
    # Credenciales del superusuario
    username = 'admin'
    email = 'admin@scontable.com'
    password = 'Admin123!'
    
    try:
        # Verificar si ya existe
        if User.objects.filter(username=username).exists():
            print("⚠️  El superusuario ya existe")
            user = User.objects.get(username=username)
            print(f"📍 Usuario: {user.username}")
            print(f"📍 Email: {user.email}")
            print(f"📍 Activo: {'Sí' if user.is_active else 'No'}")
            print(f"📍 Superusuario: {'Sí' if user.is_superuser else 'No'}")
            
            # Actualizar contraseña del usuario existente
            print("\n🔄 ACTUALIZANDO CONTRASEÑA...")
            user.set_password(password)
            user.save()
            print(f"✅ Contraseña actualizada para: {username}")
            print(f"🔑 Nueva contraseña: {password}")
        else:
            # Crear superusuario
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='Administrador',
                last_name='Sistema'
            )
            
            print("✅ ¡Superusuario creado exitosamente!")
            print(f"📍 Usuario: {username}")
            print(f"📍 Contraseña: {password}")
            print(f"📍 Email: {email}")
        
        print("\n🌐 ACCESO AL PANEL DE ADMINISTRACIÓN:")
        print("1. Ejecuta: python manage.py runserver")
        print("2. Ve a: http://127.0.0.1:8000/admin/")
        print(f"3. Inicia sesión con: {username} / {password}")
        
        print("\n💡 FUNCIONES DEL SUPERUSUARIO:")
        print("• Gestionar usuarios y perfiles")
        print("• Ver estadísticas del sistema")
        print("• Configurar parámetros")
        print("• Acceso completo a la base de datos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando superusuario: {e}")
        return False

if __name__ == '__main__':
    main()
