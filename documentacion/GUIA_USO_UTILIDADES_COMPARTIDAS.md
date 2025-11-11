# 🎓 GUÍA DE USO - NUEVAS UTILIDADES COMPARTIDAS

**Actualizado:** 11 de Noviembre de 2025  
**Para desarrolladores del proyecto FinalPoo2**

---

## 📚 NUEVOS MÓDULOS DISPONIBLES

### 1. `core/base_views.py` - Vistas Base Reutilizables

#### Vistas con Filtro de Empresa

```python
from core.base_views import (
    BaseListView, BaseDetailView, BaseCreateView, 
    BaseUpdateView, BaseDeleteView, BaseIndexView
)

# Ejemplo: Crear vista de lista de facturas
class FacturaListView(BaseListView):
    model = Factura
    template_name = 'facturacion/lista.html'
    paginate_by = 50  # Opcional, default es 50
    
    # get_queryset() ya está implementado con filtro de empresa
    # LoginRequiredMixin y EmpresaFilterMixin ya incluidos

# Ejemplo: Crear vista de creación de producto
class ProductoCreateView(BaseCreateView):
    model = Producto
    template_name = 'catalogos/producto_form.html'
    fields = ['nombre', 'precio', 'descripcion']
    success_url = reverse_lazy('catalogos:producto_list')
    
    # form_valid() ya muestra mensaje de éxito automáticamente
    # empresa_activa se asigna automáticamente si el modelo lo tiene
```

**Beneficios:**
- ✅ Menos código repetitivo
- ✅ Mensajes de éxito automáticos
- ✅ Filtro de empresa automático
- ✅ Autenticación incluida

#### Vistas Sin Filtro de Empresa

```python
from core.base_views import (
    SimpleListView, SimpleDetailView, SimpleCreateView,
    SimpleUpdateView, SimpleDeleteView
)

# Usar cuando NO se necesita filtro por empresa
class UsuarioListView(SimpleListView):
    model = User
    template_name = 'accounts/usuario_lista.html'
```

---

### 2. `core/constants.py` - Constantes Centralizadas

#### Mensajes de Error

```python
from core.constants import (
    MSG_NO_PERMISOS,
    MSG_SELECCIONAR_EMPRESA,
    MSG_ERROR_GENERICO,
    MSG_CAMPOS_REQUERIDOS
)

# Uso en vistas
def mi_vista(request):
    if not request.user.has_perm('app.permiso'):
        messages.error(request, MSG_NO_PERMISOS)
        return redirect('login')
```

#### Mensajes de Éxito

```python
from core.constants import (
    MSG_CREADO_EXITOSAMENTE,
    MSG_ACTUALIZADO_EXITOSAMENTE,
    MSG_ELIMINADO_EXITOSAMENTE
)

# Uso con formato
messages.success(request, MSG_CREADO_EXITOSAMENTE.format('Producto'))
# Resultado: "Producto creado exitosamente."
```

#### URLs Comunes

```python
from core.constants import (
    URL_LOGIN,
    URL_DASHBOARD,
    URL_ADMIN_DASHBOARD,
    URL_CAMBIAR_EMPRESA
)

# Uso en redirecciones
if not request.user.is_authenticated:
    return redirect(URL_LOGIN)
```

#### Estilos CSS

```python
from core.constants import (
    STYLE_MUTED_TEXT,
    STYLE_SUCCESS_TEXT,
    STYLE_ERROR_TEXT
)

# Uso en templates o mensajes HTML
mensaje = f'<span style="{STYLE_SUCCESS_TEXT}">Operación exitosa</span>'
```

---

### 3. `core/utils.py` - Utilidades Compartidas

#### Estadísticas de Usuarios

```python
from core.utils import get_user_stats

# En cualquier vista o función
stats = get_user_stats()

# Retorna:
# {
#     'total_users': 150,
#     'active_users': 120,
#     'inactive_users': 30,
#     'total_profiles': 145,
#     'admin_users': 5,
#     'staff_users': 10
# }

# Uso en context de template
def mi_vista(request):
    context = {
        'stats': get_user_stats(),
        # ...
    }
    return render(request, 'template.html', context)
```

#### Estadísticas de Empresas

```python
from core.utils import get_empresa_stats

empresa_stats = get_empresa_stats()
# {
#     'total_companies': 25,
#     'active_companies': 20,
#     'inactive_companies': 5
# }
```

#### Estadísticas Completas

```python
from core.utils import get_complete_stats

# Obtiene TODAS las estadísticas en una sola llamada
all_stats = get_complete_stats()

# Retorna:
# {
#     'total_users': 150,
#     'active_users': 120,
#     'inactive_users': 30,
#     'total_profiles': 145,
#     'admin_users': 5,
#     'staff_users': 10,
#     'total_companies': 25,
#     'active_companies': 20,
#     'inactive_companies': 5,
#     'recent_users': <QuerySet>,
#     'cities_stats': [...],
#     'doc_types_stats': [...]
# }
```

#### Validaciones

```python
from core.utils import validate_user_data, validate_password

# Validar datos de usuario
is_valid, error_msg = validate_user_data('juan.perez', 'juan@example.com')
if not is_valid:
    messages.error(request, error_msg)
    return redirect('registro')

# Validar contraseña
is_valid, error_msg = validate_password('Password123', 'Password123')
if not is_valid:
    messages.error(request, error_msg)
```

#### Filtros Dinámicos

```python
from core.utils import build_queryset_filters

# Construir filtros desde request.GET
queryset = Factura.objects.all()

filters = {
    'cliente__razon_social__icontains': request.GET.get('cliente'),
    'fecha_factura__gte': request.GET.get('fecha_desde'),
    'fecha_factura__lte': request.GET.get('fecha_hasta'),
    'estado': request.GET.get('estado'),
}

queryset = build_queryset_filters(queryset, filters)
# Retorna queryset filtrado (ignora valores None/vacíos automáticamente)
```

---

## 🎯 EJEMPLOS PRÁCTICOS

### Ejemplo 1: Vista de Lista Completa

```python
# facturacion/views.py
from django.urls import reverse_lazy
from core.base_views import BaseListView
from .models import Factura

class FacturaListView(BaseListView):
    model = Factura
    template_name = 'facturacion/lista.html'
    context_object_name = 'facturas'
    paginate_by = 50
    
    def get_queryset(self):
        # Llamar al padre para obtener queryset base con filtro de empresa
        queryset = super().get_queryset()
        
        # Agregar filtros personalizados
        cliente = self.request.GET.get('cliente')
        if cliente:
            queryset = queryset.filter(cliente__razon_social__icontains=cliente)
        
        return queryset.select_related('cliente').order_by('-fecha_factura')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_facturas'] = self.get_queryset().count()
        return context
```

### Ejemplo 2: Vista de Creación con Validación

```python
# catalogos/views.py
from django.urls import reverse_lazy
from core.base_views import BaseCreateView
from core.constants import MSG_CAMPOS_REQUERIDOS
from .models import Producto

class ProductoCreateView(BaseCreateView):
    model = Producto
    template_name = 'catalogos/producto_form.html'
    fields = ['codigo', 'nombre', 'precio', 'impuesto']
    success_url = reverse_lazy('catalogos:producto_list')
    
    def form_valid(self, form):
        # Validaciones personalizadas
        if form.cleaned_data['precio'] <= 0:
            messages.error(self.request, 'El precio debe ser mayor a cero.')
            return self.form_invalid(form)
        
        # Llamar al padre (asigna empresa automáticamente y muestra mensaje)
        return super().form_valid(form)
```

### Ejemplo 3: Dashboard con Estadísticas

```python
# empresas/views.py
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from core.utils import get_complete_stats

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'empresas/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener todas las estadísticas en una línea
        context.update(get_complete_stats())
        
        # Agregar datos adicionales específicos
        context['title'] = 'Dashboard Principal'
        
        return context
```

### Ejemplo 4: Vista con Constantes

```python
# tesoreria/views.py
from django.shortcuts import redirect
from django.contrib import messages
from core.base_views import BaseCreateView
from core.constants import (
    MSG_SELECCIONAR_EMPRESA,
    URL_CAMBIAR_EMPRESA,
    MSG_CREADO_EXITOSAMENTE
)

class PagoCreateView(BaseCreateView):
    model = Pago
    template_name = 'tesoreria/pago_form.html'
    fields = ['tercero', 'valor', 'metodo_pago']
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar empresa activa
        if not getattr(request, 'empresa_activa', None):
            messages.error(request, MSG_SELECCIONAR_EMPRESA)
            return redirect(URL_CAMBIAR_EMPRESA)
        
        return super().dispatch(request, *args, **kwargs)
```

---

## 🔧 MEJORES PRÁCTICAS

### ✅ DO (Hacer)

```python
# 1. Usar vistas base cuando sea posible
from core.base_views import BaseListView

class MiListaView(BaseListView):
    model = MiModelo
    # ...

# 2. Usar constantes en lugar de strings hardcodeados
from core.constants import MSG_NO_PERMISOS

messages.error(request, MSG_NO_PERMISOS)

# 3. Usar utilidades para estadísticas
from core.utils import get_complete_stats

stats = get_complete_stats()

# 4. Reutilizar validaciones
from core.utils import validate_user_data

is_valid, error = validate_user_data(username, email)
```

### ❌ DON'T (No hacer)

```python
# 1. No repetir código de vistas genéricas
# ❌ MAL
class MiListaView(LoginRequiredMixin, ListView):
    model = MiModelo
    # ... código repetitivo

# ✅ BIEN
from core.base_views import BaseListView
class MiListaView(BaseListView):
    model = MiModelo

# 2. No hardcodear strings repetidos
# ❌ MAL
messages.error(request, 'No tienes permisos...')

# ✅ BIEN
from core.constants import MSG_NO_PERMISOS
messages.error(request, MSG_NO_PERMISOS)

# 3. No duplicar lógica de estadísticas
# ❌ MAL
total_users = User.objects.count()
active_users = User.objects.filter(is_active=True).count()
# ...

# ✅ BIEN
from core.utils import get_user_stats
stats = get_user_stats()
```

---

## 📋 CHECKLIST PARA NUEVAS VISTAS

Al crear una nueva vista, verifica:

- [ ] ¿Necesito autenticación? → Usa `BaseXXXView` o `LoginRequiredMixin`
- [ ] ¿Necesito filtro por empresa? → Usa `BaseXXXView` (ya lo incluye)
- [ ] ¿Necesito mensajes de éxito? → Usa `BaseXXXView` (ya los incluye)
- [ ] ¿Uso URLs hardcodeadas? → Importa de `core.constants`
- [ ] ¿Uso mensajes hardcodeados? → Importa de `core.constants`
- [ ] ¿Necesito estadísticas? → Usa funciones de `core.utils`
- [ ] ¿Hago validaciones comunes? → Usa funciones de `core.utils`

---

## 🧪 TESTING

### Test de Vistas Base

```python
from django.test import TestCase
from django.contrib.auth.models import User
from core.base_views import BaseListView
from .models import MiModelo

class BaseViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@test.com', 'password')
        
    def test_list_view_requires_login(self):
        response = self.client.get('/mi-lista/')
        self.assertEqual(response.status_code, 302)  # Redirect a login
        
    def test_list_view_authenticated(self):
        self.client.login(username='test', password='password')
        response = self.client.get('/mi-lista/')
        self.assertEqual(response.status_code, 200)
```

### Test de Utilidades

```python
from django.test import TestCase
from core.utils import get_user_stats, validate_user_data

class UtilsTestCase(TestCase):
    def test_get_user_stats(self):
        stats = get_user_stats()
        self.assertIn('total_users', stats)
        self.assertIsInstance(stats['total_users'], int)
        
    def test_validate_user_data_valid(self):
        is_valid, error = validate_user_data('juan', 'juan@test.com')
        self.assertTrue(is_valid)
        self.assertIsNone(error)
```

---

## 🚀 MIGRACIÓN DE CÓDIGO EXISTENTE

### Paso 1: Identificar vista a migrar

```python
# ANTES
class ProductoListView(LoginRequiredMixin, EmpresaFilterMixin, ListView):
    model = Producto
    template_name = 'catalogos/producto_lista.html'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('nombre')
```

### Paso 2: Importar vista base

```python
from core.base_views import BaseListView
```

### Paso 3: Refactorizar

```python
# DESPUÉS
class ProductoListView(BaseListView):
    model = Producto
    template_name = 'catalogos/producto_lista.html'
    # paginate_by ya es 50 por defecto en BaseListView
    
    def get_queryset(self):
        queryset = super().get_queryset()  # Ya incluye filtro de empresa
        return queryset.order_by('nombre')
```

### Paso 4: Verificar

- [ ] Tests pasan
- [ ] Vista funciona correctamente
- [ ] Mensajes de éxito aparecen
- [ ] Filtro de empresa funciona

---

## 📞 SOPORTE

Si tienes dudas sobre el uso de estas utilidades:

1. Revisa los ejemplos en esta guía
2. Mira el código en `core/base_views.py`, `core/constants.py`, `core/utils.py`
3. Busca ejemplos de uso en archivos ya refactorizados:
   - `catalogos/views.py`
   - `tesoreria/views.py`
   - `empresas/views_admin.py`

---

**¡Happy Coding!** 🎉
