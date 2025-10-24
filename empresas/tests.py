from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Empresa, PerfilEmpresa, EmpresaActiva


class EmpresaModelTest(TestCase):
    """Tests para el modelo Empresa"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_crear_empresa(self):
        """Test para crear una empresa"""
        empresa = Empresa.objects.create(
            nit='123456789-0',
            razon_social='Test Company SAS',
            tipo_empresa='SAS',
            direccion='Calle 123 #45-67',
            ciudad='Bogotá',
            telefono='3001234567',
            email='empresa@test.com',
            propietario=self.user
        )
        
        self.assertEqual(empresa.razon_social, 'Test Company SAS')
        self.assertEqual(empresa.nit, '123456789-0')
        self.assertTrue(empresa.activa)
        self.assertEqual(str(empresa), 'Test Company SAS (123456789-0)')
    
    def test_nit_formateado(self):
        """Test para el formato del NIT"""
        empresa = Empresa.objects.create(
            nit='123456789-0',
            razon_social='Test Company SAS',
            direccion='Calle 123',
            ciudad='Bogotá',
            telefono='3001234567',
            email='empresa@test.com',
            propietario=self.user
        )
        
        # El método nit_formateado debería formatear correctamente
        self.assertIsNotNone(empresa.nit_formateado)


class PerfilEmpresaModelTest(TestCase):
    """Tests para el modelo PerfilEmpresa"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.empresa = Empresa.objects.create(
            nit='123456789-0',
            razon_social='Test Company SAS',
            direccion='Calle 123',
            ciudad='Bogotá',
            telefono='3001234567',
            email='empresa@test.com',
            propietario=self.admin_user
        )
    
    def test_crear_perfil_empresa(self):
        """Test para crear un perfil de empresa"""
        perfil = PerfilEmpresa.objects.create(
            usuario=self.user,
            empresa=self.empresa,
            rol='contador',
            asignado_por=self.admin_user
        )
        
        self.assertEqual(perfil.rol, 'contador')
        self.assertTrue(perfil.activo)
        self.assertFalse(perfil.puede_administrar)
        self.assertTrue(perfil.puede_confirmar_documentos)
        self.assertFalse(perfil.solo_lectura_reportes)
    
    def test_roles_permisos(self):
        """Test para verificar permisos por rol"""
        # Perfil admin
        perfil_admin = PerfilEmpresa.objects.create(
            usuario=self.admin_user,
            empresa=self.empresa,
            rol='admin',
            asignado_por=self.admin_user
        )
        
        self.assertTrue(perfil_admin.puede_administrar)
        self.assertTrue(perfil_admin.puede_confirmar_documentos)
        self.assertFalse(perfil_admin.solo_lectura_reportes)
        
        # Perfil operador
        perfil_operador = PerfilEmpresa.objects.create(
            usuario=self.user,
            empresa=self.empresa,
            rol='operador',
            asignado_por=self.admin_user
        )
        
        self.assertFalse(perfil_operador.puede_administrar)
        self.assertFalse(perfil_operador.puede_confirmar_documentos)
        self.assertTrue(perfil_operador.solo_lectura_reportes)
    
    def test_unique_usuario_empresa(self):
        """Test para verificar que un usuario solo puede tener un perfil por empresa"""
        PerfilEmpresa.objects.create(
            usuario=self.user,
            empresa=self.empresa,
            rol='contador',
            asignado_por=self.admin_user
        )
        
        # Intentar crear otro perfil para el mismo usuario y empresa debería fallar
        with self.assertRaises(Exception):
            PerfilEmpresa.objects.create(
                usuario=self.user,
                empresa=self.empresa,
                rol='admin',
                asignado_por=self.admin_user
            )


class EmpresaActivaModelTest(TestCase):
    """Tests para el modelo EmpresaActiva"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.empresa = Empresa.objects.create(
            nit='123456789-0',
            razon_social='Test Company SAS',
            direccion='Calle 123',
            ciudad='Bogotá',
            telefono='3001234567',
            email='empresa@test.com',
            propietario=self.user
        )
    
    def test_crear_empresa_activa(self):
        """Test para crear una empresa activa"""
        empresa_activa = EmpresaActiva.objects.create(
            usuario=self.user,
            empresa=self.empresa
        )
        
        self.assertEqual(empresa_activa.usuario, self.user)
        self.assertEqual(empresa_activa.empresa, self.empresa)
        self.assertIsNotNone(empresa_activa.fecha_seleccion)
    
    def test_unique_usuario(self):
        """Test para verificar que un usuario solo puede tener una empresa activa"""
        EmpresaActiva.objects.create(
            usuario=self.user,
            empresa=self.empresa
        )
        
        # Crear otra empresa
        otra_empresa = Empresa.objects.create(
            nit='987654321-0',
            razon_social='Another Company SAS',
            direccion='Calle 456',
            ciudad='Medellín',
            telefono='3009876543',
            email='otra@test.com',
            propietario=self.user
        )
        
        # Intentar crear otra empresa activa debería reemplazar la anterior
        nueva_activa = EmpresaActiva.objects.create(
            usuario=self.user,
            empresa=otra_empresa
        )
        
        # Debería haber solo una empresa activa por usuario
        self.assertEqual(EmpresaActiva.objects.filter(usuario=self.user).count(), 1)
        self.assertEqual(nueva_activa.empresa, otra_empresa)
