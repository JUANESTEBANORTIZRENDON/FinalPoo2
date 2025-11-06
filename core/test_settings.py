"""
Configuración compartida para tests
Centraliza valores de prueba para evitar hardcoding en múltiples archivos
"""
import os
from django.conf import settings

# Contraseñas de prueba
# En producción, estas se cargan desde variables de entorno
TEST_USER_PASSWORD = os.getenv('TEST_USER_PASSWORD', 'T3stP@ss2024!')
TEST_ADMIN_PASSWORD = os.getenv('TEST_ADMIN_PASSWORD', 'Adm1nP@ss2024!')

# Datos de prueba para usuarios
TEST_USER_DATA = {
    'username': 'testuser',
    'email': 'test@example.com',
    'password': TEST_USER_PASSWORD
}

TEST_ADMIN_DATA = {
    'username': 'admin',
    'email': 'admin@example.com',
    'password': TEST_ADMIN_PASSWORD
}

# Datos de prueba para empresa
TEST_EMPRESA_DATA = {
    'nit': '123456789-0',
    'razon_social': 'Test Company SAS',
    'direccion': 'Calle 123',
    'ciudad': 'Bogotá',
    'telefono': '3001234567',
    'email': 'empresa@test.com'
}
