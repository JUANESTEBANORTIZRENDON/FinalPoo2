from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.core.signing import Signer
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .forms import RegistroCompletoForm

# Constantes para URLs reutilizables
LOGIN_URL_NAME = 'accounts:login'
ADMIN_URL_PATH = '/admin/'
DASHBOARD_URL_NAME = 'accounts:dashboard'

class RegisterView(CreateView):
    """Vista para el registro completo de usuarios colombianos"""
    form_class = RegistroCompletoForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy(LOGIN_URL_NAME)
    
    def form_valid(self, form):
        """Procesar registro y enviar email de activación"""
        # Guardar usuario (se crea inactivo)
        user = form.save()
        
        # Generar token de activación
        signer = Signer()
        token = signer.sign(f"{user.id}:{user.email}")
        
        # Enviar email de activación (OBLIGATORIO)
        try:
            subject = '🎉 ¡Bienvenido a S_CONTABLE! Activa tu cuenta'
            
            # Información personalizada del perfil
            perfil = user.perfil
            nombre_completo = f"{user.first_name} {user.last_name}".strip()
            documento = perfil.documento_completo if perfil.numero_documento else "No especificado"
            ciudad = f"{perfil.ciudad}, {perfil.departamento}" if perfil.ciudad else "Colombia"
            
            message = f"""
¡Hola {nombre_completo}!

¡Bienvenido/a a S_CONTABLE - Tu Sistema Contable Colombiano! 🇨🇴

Gracias por registrarte con nosotros. Hemos recibido tu información:

👤 INFORMACIÓN REGISTRADA:
• Nombre: {nombre_completo}
• Documento: {documento}
• Email: {user.email}
• Teléfono: {perfil.telefono or 'No especificado'}
• Ubicación: {ciudad}
• Profesión: {perfil.profesion or 'No especificada'}

📧 ACTIVACIÓN REQUERIDA:
Para completar tu registro y activar tu cuenta, haz clic en el siguiente enlace:

🌐 ACTIVAR CUENTA:
http://127.0.0.1:8000/accounts/activar/?token={token}

⏰ IMPORTANTE:
- Este enlace expira en 24 horas por tu seguridad
- Solo puedes usar este enlace una vez
- Si no te registraste, ignora este email

🔒 PRIVACIDAD:
Tu información está protegida según nuestra política de privacidad.
Solo será usada para brindarte el mejor servicio contable.

¿Necesitas ayuda? Responde a este email.

¡Esperamos que disfrutes usando S_CONTABLE para gestionar tu contabilidad!

Cordialmente,
El equipo de S_CONTABLE 🚀

---
S_CONTABLE - Sistema Contable Colombiano
Tu aliado en gestión financiera y contable
            """
            
            # Intentar enviar email (OBLIGATORIO - no fail_silently)
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            messages.success(
                self.request, 
                f'¡Cuenta creada exitosamente! Se ha enviado un email de activación a {user.email}. '
                'Revisa tu correo para activar tu cuenta.'
            )
            
        except Exception as e:
            # Si falla el email, eliminar usuario y mostrar error
            user.delete()
            messages.error(
                self.request,
                f'Error al enviar email de activación: {str(e)}. '
                f'Por favor, verifica tu email y intenta nuevamente. '
                f'Si el problema persiste, contacta al administrador.'
            )
            return self.form_invalid(form)
        
        return redirect(self.success_url)
    
    def dispatch(self, request, *args, **kwargs):
        # Si el usuario ya está autenticado, redirigir según su tipo
        if request.user.is_authenticated:
            if request.user.is_superuser or request.user.is_staff:
                # Administradores van al panel admin
                return redirect(ADMIN_URL_PATH)
            else:
                # Usuarios normales van al dashboard
                return redirect(DASHBOARD_URL_NAME)
        return super().dispatch(request, *args, **kwargs)

class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Vista del dashboard principal del usuario con información contable
    """
    template_name = 'accounts/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_profile'] = getattr(self.request.user, 'perfil', None)
        
        # Información de la empresa activa
        empresa_activa = getattr(self.request, 'empresa_activa', None)
        
        # Debug: verificar si hay empresas y perfiles
        from empresas.models import Empresa, PerfilEmpresa
        
        empresas_disponibles = Empresa.objects.filter(
            perfiles__usuario=self.request.user,
            perfiles__activo=True,
            activa=True
        ).distinct()
        
        context['debug_empresas_count'] = empresas_disponibles.count()
        context['debug_tiene_empresa_activa'] = empresa_activa is not None
        
        if empresa_activa:
            context['empresa_activa'] = empresa_activa
            context['rol_empresa'] = getattr(self.request, 'rol_empresa', None)
            
            # Estadísticas básicas del dashboard
            context.update(self.get_dashboard_stats(empresa_activa))
        else:
            # Si no hay empresa activa, verificar por qué
            perfiles = PerfilEmpresa.objects.filter(
                usuario=self.request.user,
                activo=True
            )
            context['debug_perfiles_count'] = perfiles.count()
        
        return context
    
    def get_dashboard_stats(self, empresa):
        """
        Obtiene estadísticas básicas para el dashboard
        """
        from catalogos.models import Tercero, Producto
        from facturacion.models import Factura
        from tesoreria.models import Pago
        from contabilidad.models import CuentaContable, Asiento
        from django.db.models import Count, Sum
        from django.utils import timezone
        from datetime import datetime, timedelta
        
        # Fecha actual y rangos
        hoy = timezone.now().date()
        inicio_mes = hoy.replace(day=1)
        
        stats = {}
        
        try:
            # Estadísticas de catálogos
            stats['total_clientes'] = Tercero.objects.filter(
                empresa=empresa,
                tipo_tercero__in=['cliente', 'ambos'],
                activo=True
            ).count()
            
            stats['total_productos'] = Producto.objects.filter(
                empresa=empresa,
                activo=True
            ).count()
            
            # Estadísticas de facturación
            facturas_mes = Factura.objects.filter(
                empresa=empresa,
                fecha_factura__gte=inicio_mes,
                estado='confirmada'
            )
            
            stats['facturas_mes'] = facturas_mes.count()
            stats['ventas_mes'] = facturas_mes.aggregate(
                total=Sum('total')
            )['total'] or 0
            
            # Facturas pendientes
            stats['facturas_pendientes'] = Factura.objects.filter(
                empresa=empresa,
                estado='borrador'
            ).count()
            
            # Estadísticas de tesorería
            cobros_mes = Pago.objects.filter(
                empresa=empresa,
                tipo_pago='cobro',
                fecha_pago__gte=inicio_mes,
                estado='confirmado'
            )
            
            stats['cobros_mes'] = cobros_mes.aggregate(
                total=Sum('valor')
            )['total'] or 0
            
            # Estadísticas de contabilidad
            stats['total_cuentas'] = CuentaContable.objects.filter(
                empresa=empresa,
                activa=True
            ).count()
            
            stats['asientos_mes'] = Asiento.objects.filter(
                empresa=empresa,
                fecha_asiento__gte=inicio_mes
            ).count()
            
            # Últimas actividades
            stats['ultimas_facturas'] = Factura.objects.filter(
                empresa=empresa
            ).order_by('-fecha_creacion')[:5]
            
            stats['ultimos_pagos'] = Pago.objects.filter(
                empresa=empresa
            ).order_by('-fecha_creacion')[:5]
            
        except Exception as e:
            # En caso de error, devolver estadísticas vacías
            stats = {
                'total_clientes': 0,
                'total_productos': 0,
                'facturas_mes': 0,
                'ventas_mes': 0,
                'facturas_pendientes': 0,
                'cobros_mes': 0,
                'total_cuentas': 0,
                'asientos_mes': 0,
                'ultimas_facturas': [],
                'ultimos_pagos': [],
            }
        
        return stats


class CustomLoginView(LoginView):
    """Vista de login personalizada con redirección inteligente"""
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        """Redirigir según el tipo de usuario"""
        user = self.request.user
        
        if user.is_superuser or user.is_staff:
            # Administradores van al panel admin
            return ADMIN_URL_PATH
        else:
            # Usuarios normales van al dashboard
            return reverse_lazy(DASHBOARD_URL_NAME)
    
    def dispatch(self, request, *args, **kwargs):
        # Si ya está autenticado, redirigir según su tipo
        if request.user.is_authenticated:
            if request.user.is_superuser or request.user.is_staff:
                return redirect(ADMIN_URL_PATH)
            else:
                return redirect(DASHBOARD_URL_NAME)
        return super().dispatch(request, *args, **kwargs)


def activar_cuenta(request):
    """Vista para activar cuenta mediante token"""
    token = request.GET.get('token')
    
    if not token:
        messages.error(request, 'Token de activación no válido.')
        return redirect(LOGIN_URL_NAME)
    
    try:
        signer = Signer()
        data = signer.unsign(token)
        user_id, email = data.split(':')
        
        user = User.objects.get(id=user_id, email=email)
        
        if user.is_active:
            messages.info(request, 'Tu cuenta ya está activada. Puedes iniciar sesión.')
        else:
            user.is_active = True
            user.save()
            messages.success(request, '¡Cuenta activada exitosamente! Ya puedes iniciar sesión.')
        
        return redirect(LOGIN_URL_NAME)
        
    except Exception as e:
        messages.error(request, f'Error al activar cuenta: {str(e)}')
        return redirect(LOGIN_URL_NAME)


class CustomLogoutView(LogoutView):
    """Vista de logout personalizada"""
    next_page = LOGIN_URL_NAME
    
    def dispatch(self, request, *args, **kwargs):
        """Limpiar sesión completamente"""
        if request.user.is_authenticated:
            # Limpiar empresa activa de la sesión
            if 'empresa_activa_id' in request.session:
                del request.session['empresa_activa_id']
            
            # Limpiar cualquier otra información de sesión
            request.session.flush()
            
            # Hacer logout
            logout(request)
            
            messages.success(request, 'Has cerrado sesión exitosamente.')
        
        return redirect(self.next_page)
