# Standard library imports
from urllib.parse import urlparse, urljoin

# Django imports
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy, resolve, reverse, NoReverseMatch
from django.utils import timezone
from django.conf import settings
from django.utils.http import url_has_allowed_host_and_scheme

# Project imports
from .models import Empresa, PerfilEmpresa, HistorialCambioEmpresa

# URL constants
ACCOUNTS_DASHBOARD_URL = 'accounts:dashboard'


class EmpresaListView(LoginRequiredMixin, ListView):
    model = Empresa
    template_name = 'empresas/empresa_list.html'
    context_object_name = 'object_list'
    
    def get_queryset(self):
        # Solo mostrar empresas donde el usuario tiene perfiles
        return Empresa.objects.filter(
            perfiles__usuario=self.request.user,
            perfiles__activo=True
        ).distinct()

class EmpresaDetailView(LoginRequiredMixin, DetailView):
    model = Empresa
    template_name = 'empresas/empresa_detail.html'

class EmpresaCreateView(LoginRequiredMixin, CreateView):
    model = Empresa
    template_name = 'empresas/empresa_form.html'
    fields = ['nit', 'razon_social', 'tipo_empresa', 'direccion', 'ciudad', 'telefono', 'email']
    success_url = reverse_lazy('empresas:empresa_list')
    
    def form_valid(self, form):
        form.instance.propietario = self.request.user
        response = super().form_valid(form)
        
        # Crear perfil de admin para el propietario
        PerfilEmpresa.objects.create(
            usuario=self.request.user,
            empresa=self.object,
            rol='admin',
            asignado_por=self.request.user
        )
        
        messages.success(self.request, f'Empresa {self.object.razon_social} creada exitosamente.')
        return response

class EmpresaUpdateView(LoginRequiredMixin, UpdateView):
    model = Empresa
    template_name = 'empresas/empresa_form.html'
    fields = ['nit', 'razon_social', 'tipo_empresa', 'direccion', 'ciudad', 'telefono', 'email']
    success_url = reverse_lazy('empresas:empresa_list')

class PerfilEmpresaListView(LoginRequiredMixin, ListView):
    model = PerfilEmpresa
    template_name = 'empresas/perfil_list.html'
    
    def get_queryset(self):
        empresa_id = self.kwargs.get('empresa_pk')
        return PerfilEmpresa.objects.filter(empresa_id=empresa_id)

class PerfilEmpresaCreateView(LoginRequiredMixin, CreateView):
    model = PerfilEmpresa
    template_name = 'empresas/perfil_form.html'
    fields = ['usuario', 'rol']
    
    def form_valid(self, form):
        empresa_id = self.kwargs.get('empresa_pk')
        form.instance.empresa_id = empresa_id
        form.instance.asignado_por = self.request.user
        return super().form_valid(form)

class PerfilEmpresaUpdateView(LoginRequiredMixin, UpdateView):
    model = PerfilEmpresa
    template_name = 'empresas/perfil_form.html'
    fields = ['rol', 'activo']

class PerfilEmpresaDeleteView(LoginRequiredMixin, DeleteView):
    model = PerfilEmpresa
    template_name = 'empresas/perfil_confirm_delete.html'

class CambiarEmpresaView(LoginRequiredMixin, TemplateView):
    template_name = 'empresas/cambiar_empresa.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener empresas donde el usuario tiene perfiles activos
        empresas = Empresa.objects.filter(
            perfiles__usuario=self.request.user,
            perfiles__activo=True,
            activa=True
        ).distinct()
        
        # Obtener empresa activa actual
        try:
            empresa_activa = EmpresaActiva.objects.get(usuario=self.request.user).empresa
        except EmpresaActiva.DoesNotExist:
            empresa_activa = None
        
        context.update({
            'empresas': empresas,
            'empresa_activa': empresa_activa
        })
        return context

def is_safe_url(url, allowed_hosts=None, require_https=False):
    """
    Return the url if it's a safe redirection (i.e. it doesn't point to a different host).
    Returns None if the URL is not safe.
    """
    if url is None or not isinstance(url, str):
        return None
        
    # Remove any whitespace and check for empty string
    url = url.strip()
    if not url:
        return None
    
    # If it's a relative URL, resolve it against the current host
    if url.startswith('/'):
        # Use Django's built-in resolver to check if it's a valid URL pattern
        try:
            # This will raise NoReverseMatch if the URL is not a valid pattern
            resolve(url)
            return url
        except Exception:
            return None
    
    # For absolute URLs, use Django's built-in security check
    if url_has_allowed_host_and_scheme(
        url=url,
        allowed_hosts=allowed_hosts,
        require_https=require_https
    ):
        return url
        
    return None

@require_http_methods(["POST"])
@login_required
def seleccionar_empresa(request):
    empresa_id = request.POST.get('empresa_id')
    next_url = request.POST.get('next', '')
    
    # Validate next_url - only allow relative URLs or URLs in ALLOWED_HOSTS
    next_url = is_safe_url(next_url, allowed_hosts=set(settings.ALLOWED_HOSTS)) or ACCOUNTS_DASHBOARD_URL
    
    if empresa_id:
        try:
                # Verificar que el usuario tiene acceso a esta empresa
                empresa = get_object_or_404(
                    Empresa,
                    id=empresa_id,
                    perfiles__usuario=request.user,
                    perfiles__activo=True
                )
                
                # Obtener o crear el perfil de empresa
                perfil = get_object_or_404(
                    PerfilEmpresa,
                    empresa=empresa,
                    usuario=request.user,
                    activo=True
                )
                
                # Actualizar o crear empresa activa
                empresa_activa, _ = EmpresaActiva.objects.update_or_create(
                    usuario=request.user,
                    defaults={
                        'empresa': empresa,
                        'fecha_actualizacion': timezone.now()
                    }
                )
                
                # Actualizar la sesión
                request.session['empresa_activa_id'] = empresa.id
                request.session['empresa_activa_nombre'] = empresa.razon_social
                request.session['rol_empresa'] = perfil.rol
                
                # Asegurarse de que los cambios se guarden en la sesión
                request.session.modified = True
                
                # Registrar el cambio de empresa en el historial
                try:
                    HistorialCambios.registrar_accion(
                        usuario=request.user,
                        tipo_accion='usuario_cambio_empresa',
                        descripcion=f'Cambio de empresa activa a: {empresa.razon_social}',
                        empresa=empresa,
                        request=request
                    )
                except Exception as e:
                    # Si hay un error al registrar en el historial, solo mostrarlo en consola
                    # para no interrumpir el flujo principal
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f'Error al registrar cambio de empresa en el historial: {str(e)}', exc_info=True)
                
                messages.success(
                    request, 
                    f'Empresa activa cambiada a: {empresa.razon_social}'
                )
                
                # Redirigir al dashboard específico del rol o a la URL de origen
                return redirect(next_url or ACCOUNTS_DASHBOARD_URL)
                
            except (Empresa.DoesNotExist, PerfilEmpresa.DoesNotExist):
                messages.error(request, 'No tienes acceso a esta empresa.')
        else:
            messages.error(request, 'Empresa no especificada.')
    
    # Redirigir al dashboard por defecto si algo falla
    return redirect(ACCOUNTS_DASHBOARD_URL)
