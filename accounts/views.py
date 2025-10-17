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
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from .forms import RegistroCompletoForm

# Constantes para URLs reutilizables
LOGIN_URL_NAME = 'accounts:login'

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
                return redirect('/admin/')
            else:
                # Usuarios normales van al dashboard
                return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)

class DashboardView(LoginRequiredMixin, TemplateView):
    """Vista del dashboard principal después del login"""
    template_name = 'accounts/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class CustomLoginView(LoginView):
    """Vista de login personalizada con redirección inteligente"""
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        """Redirigir según el tipo de usuario"""
        user = self.request.user
        
        if user.is_superuser or user.is_staff:
            # Administradores van al panel admin
            return '/admin/'
        else:
            # Usuarios normales van al dashboard
            return reverse_lazy('accounts:dashboard')
    
    def dispatch(self, request, *args, **kwargs):
        # Si ya está autenticado, redirigir según su tipo
        if request.user.is_authenticated:
            if request.user.is_superuser or request.user.is_staff:
                return redirect('/admin/')
            else:
                return redirect('accounts:dashboard')
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
        messages.error(request, 'Token de activación inválido o expirado.')
        return redirect(LOGIN_URL_NAME)
