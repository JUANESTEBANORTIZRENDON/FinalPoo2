from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from .models import CuentaContable, Asiento, Partida
from .services import ServicioContabilidad, ServicioPlanCuentas
from empresas.models import Empresa
from catalogos.models import Tercero, Impuesto, MetodoPago, Producto
from facturacion.models import Factura, FacturaDetalle
from tesoreria.models import Pago
from core.test_settings import TEST_USER_PASSWORD


class ServicioContabilidadTest(TestCase):
    """Tests para el servicio de contabilidad"""
    
    def setUp(self):
        # Crear usuario y empresa
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password=TEST_USER_PASSWORD
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
        
        # Crear plan de cuentas básico
        ServicioPlanCuentas.crear_plan_cuentas_basico(self.empresa, self.user)
        
        # Crear tercero (cliente)
        self.cliente = Tercero.objects.create(
            empresa=self.empresa,
            tipo_tercero='cliente',
            numero_documento='12345678',
            razon_social='Cliente Test',
            direccion='Calle Cliente 123',
            ciudad='Bogotá',
            telefono='3001111111',
            email='cliente@test.com'
        )
        
        # Crear impuesto
        self.impuesto = Impuesto.objects.create(
            empresa=self.empresa,
            codigo='IVA19',
            nombre='IVA 19%',
            tipo_impuesto='IVA',
            porcentaje=Decimal('19.00')
        )
        
        # Crear método de pago
        self.metodo_pago = MetodoPago.objects.create(
            empresa=self.empresa,
            codigo='EFE',
            nombre='Efectivo',
            tipo_metodo='EFECTIVO'
        )
        
        # Crear producto
        self.producto = Producto.objects.create(
            empresa=self.empresa,
            codigo='PROD001',
            nombre='Producto Test',
            precio_venta=Decimal('100000.00'),
            impuesto=self.impuesto
        )
    
    def test_obtener_siguiente_numero_asiento(self):
        """Test para obtener el siguiente número de asiento"""
        numero = ServicioContabilidad.obtener_siguiente_numero_asiento(self.empresa)
        self.assertEqual(numero, '000001')
        
        # Crear un asiento
        Asiento.objects.create(
            empresa=self.empresa,
            numero_asiento='000001',
            fecha_asiento='2024-01-01',
            concepto='Test',
            creado_por=self.user
        )
        
        # El siguiente número debería ser 000002
        numero = ServicioContabilidad.obtener_siguiente_numero_asiento(self.empresa)
        self.assertEqual(numero, '000002')
    
    def test_generar_asiento_venta_contado(self):
        """Test para generar asiento de venta de contado"""
        # Crear factura de contado
        factura = Factura.objects.create(
            empresa=self.empresa,
            numero_factura='F001',
            fecha_factura='2024-01-01',
            cliente=self.cliente,
            tipo_venta='contado',
            metodo_pago=self.metodo_pago,
            subtotal=Decimal('100000.00'),
            total_impuestos=Decimal('19000.00'),
            total=Decimal('119000.00'),
            creado_por=self.user
        )
        
        # Generar asiento
        asiento = ServicioContabilidad.generar_asiento_venta(factura)
        
        # Verificar que se creó el asiento
        self.assertIsNotNone(asiento)
        self.assertEqual(asiento.empresa, self.empresa)
        self.assertEqual(asiento.tipo_asiento, 'automatico')
        self.assertEqual(asiento.estado, 'confirmado')
        
        # Verificar que está cuadrado
        self.assertTrue(asiento.esta_cuadrado)
        self.assertEqual(asiento.total_debito, asiento.total_credito)
        self.assertEqual(asiento.total_debito, Decimal('119000.00'))
        
        # Verificar partidas
        partidas = asiento.partidas.all()
        self.assertEqual(partidas.count(), 3)  # Caja, Ingresos, IVA
        
        # Verificar que la factura quedó asociada al asiento
        factura.refresh_from_db()
        self.assertEqual(factura.asiento_contable, asiento)
    
    def test_generar_asiento_venta_credito(self):
        """Test para generar asiento de venta a crédito"""
        # Crear factura a crédito
        factura = Factura.objects.create(
            empresa=self.empresa,
            numero_factura='F002',
            fecha_factura='2024-01-01',
            cliente=self.cliente,
            tipo_venta='credito',
            subtotal=Decimal('100000.00'),
            total_impuestos=Decimal('19000.00'),
            total=Decimal('119000.00'),
            creado_por=self.user
        )
        
        # Generar asiento
        asiento = ServicioContabilidad.generar_asiento_venta(factura)
        
        # Verificar que se creó el asiento
        self.assertIsNotNone(asiento)
        self.assertTrue(asiento.esta_cuadrado)
        
        # Verificar partidas (Clientes, Ingresos, IVA)
        partidas = asiento.partidas.all()
        self.assertEqual(partidas.count(), 3)
    
    def test_generar_asiento_cobro(self):
        """Test para generar asiento de cobro"""
        # Crear pago (cobro)
        pago = Pago.objects.create(
            empresa=self.empresa,
            numero_pago='C001',
            fecha_pago='2024-01-01',
            tipo_pago='cobro',
            tercero=self.cliente,
            metodo_pago=self.metodo_pago,
            valor=Decimal('119000.00'),
            creado_por=self.user
        )
        
        # Generar asiento
        asiento = ServicioContabilidad.generar_asiento_cobro(pago)
        
        # Verificar que se creó el asiento
        self.assertIsNotNone(asiento)
        self.assertTrue(asiento.esta_cuadrado)
        self.assertEqual(asiento.total_debito, Decimal('119000.00'))
        
        # Verificar partidas (Caja, Clientes)
        partidas = asiento.partidas.all()
        self.assertEqual(partidas.count(), 2)
        
        # Verificar que el pago quedó asociado al asiento
        pago.refresh_from_db()
        self.assertEqual(pago.asiento_contable, asiento)
    
    def test_no_duplicar_asientos(self):
        """Test para verificar que no se dupliquen asientos"""
        # Crear factura
        factura = Factura.objects.create(
            empresa=self.empresa,
            numero_factura='F003',
            fecha_factura='2024-01-01',
            cliente=self.cliente,
            tipo_venta='contado',
            metodo_pago=self.metodo_pago,
            subtotal=Decimal('100000.00'),
            total_impuestos=Decimal('19000.00'),
            total=Decimal('119000.00'),
            creado_por=self.user
        )
        
        # Generar asiento por primera vez
        asiento1 = ServicioContabilidad.generar_asiento_venta(factura)
        
        # Intentar generar asiento nuevamente
        asiento2 = ServicioContabilidad.generar_asiento_venta(factura)
        
        # Debería retornar el mismo asiento
        self.assertEqual(asiento1, asiento2)
        
        # Verificar que solo hay un asiento
        asientos_count = Asiento.objects.filter(empresa=self.empresa).count()
        self.assertEqual(asientos_count, 1)


class ServicioPlanCuentasTest(TestCase):
    """Tests para el servicio de plan de cuentas"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password=TEST_USER_PASSWORD
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
    
    def test_crear_plan_cuentas_basico(self):
        """Test para crear plan de cuentas básico"""
        cuentas = ServicioPlanCuentas.crear_plan_cuentas_basico(self.empresa, self.user)
        
        # Verificar que se crearon las cuentas
        self.assertGreater(len(cuentas), 0)
        
        # Verificar que existen las cuentas principales
        self.assertTrue(CuentaContable.objects.filter(
            empresa=self.empresa,
            codigo='1105'  # Caja
        ).exists())
        
        self.assertTrue(CuentaContable.objects.filter(
            empresa=self.empresa,
            codigo='1305'  # Clientes
        ).exists())
        
        self.assertTrue(CuentaContable.objects.filter(
            empresa=self.empresa,
            codigo='4135'  # Ingresos
        ).exists())
        
        self.assertTrue(CuentaContable.objects.filter(
            empresa=self.empresa,
            codigo='2408'  # IVA por pagar
        ).exists())
        
        # Verificar jerarquía
        cuenta_activo = CuentaContable.objects.get(empresa=self.empresa, codigo='1')
        cuenta_caja = CuentaContable.objects.get(empresa=self.empresa, codigo='1105')
        
        self.assertFalse(cuenta_activo.acepta_movimiento)
        self.assertTrue(cuenta_caja.acepta_movimiento)


class AsientoModelTest(TestCase):
    """Tests para el modelo Asiento"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password=TEST_USER_PASSWORD
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
        
        # Crear cuentas de prueba
        self.cuenta_caja = CuentaContable.objects.create(
            empresa=self.empresa,
            codigo='1105',
            nombre='Caja',
            naturaleza='D',
            tipo_cuenta='ACTIVO'
        )
        
        self.cuenta_ingresos = CuentaContable.objects.create(
            empresa=self.empresa,
            codigo='4135',
            nombre='Ingresos',
            naturaleza='C',
            tipo_cuenta='INGRESO'
        )
    
    def test_crear_asiento_cuadrado(self):
        """Test para crear un asiento cuadrado"""
        asiento = Asiento.objects.create(
            empresa=self.empresa,
            numero_asiento='A001',
            fecha_asiento='2024-01-01',
            concepto='Asiento de prueba',
            creado_por=self.user
        )
        
        # Crear partidas
        Partida.objects.create(
            asiento=asiento,
            cuenta=self.cuenta_caja,
            concepto='Ingreso en caja',
            valor_debito=Decimal('100000.00'),
            orden=1
        )
        
        Partida.objects.create(
            asiento=asiento,
            cuenta=self.cuenta_ingresos,
            concepto='Venta de servicios',
            valor_credito=Decimal('100000.00'),
            orden=2
        )
        
        # Recalcular totales
        asiento.calcular_totales()
        asiento.save()
        
        # Verificar que está cuadrado
        self.assertTrue(asiento.esta_cuadrado)
        self.assertEqual(asiento.total_debito, Decimal('100000.00'))
        self.assertEqual(asiento.total_credito, Decimal('100000.00'))
        self.assertTrue(asiento.puede_confirmarse)
    
    def test_asiento_descuadrado(self):
        """Test para asiento descuadrado"""
        asiento = Asiento.objects.create(
            empresa=self.empresa,
            numero_asiento='A002',
            fecha_asiento='2024-01-01',
            concepto='Asiento descuadrado',
            creado_por=self.user
        )
        
        # Crear partidas descuadradas
        Partida.objects.create(
            asiento=asiento,
            cuenta=self.cuenta_caja,
            concepto='Débito',
            valor_debito=Decimal('100000.00'),
            orden=1
        )
        
        Partida.objects.create(
            asiento=asiento,
            cuenta=self.cuenta_ingresos,
            concepto='Crédito',
            valor_credito=Decimal('50000.00'),
            orden=2
        )
        
        # Recalcular totales
        asiento.calcular_totales()
        asiento.save()
        
        # Verificar que NO está cuadrado
        self.assertFalse(asiento.esta_cuadrado)
        self.assertFalse(asiento.puede_confirmarse)
