from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from .models import Empresa, PerfilEmpresa, EmpresaActiva

# Constante para evitar duplicación del literal de URL
EMPRESA_LIST_URL = 'empresas:empresa_list'


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
    success_url = reverse_lazy(EMPRESA_LIST_URL)
    
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
    success_url = reverse_lazy(EMPRESA_LIST_URL)

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

@login_required
@require_http_methods(["POST"])
def seleccionar_empresa(request):
    if request.method == 'POST':
        empresa_id = request.POST.get('empresa_id')
        
        if empresa_id:
            try:
                # Verificar que el usuario tiene acceso a esta empresa
                empresa = get_object_or_404(
                    Empresa,
                    id=empresa_id,
                    perfiles__usuario=request.user,
                    perfiles__activo=True
                )
                
                # Actualizar o crear empresa activa
                empresa_activa, created = EmpresaActiva.objects.get_or_create(
                    usuario=request.user,
                    defaults={'empresa': empresa}
                )
                
                if not created:
                    empresa_activa.empresa = empresa
                    empresa_activa.save()
                
                # IMPORTANTE: Actualizar la sesión para que el cambio sea inmediato
                request.session['empresa_activa_id'] = empresa.id
                request.session.modified = True
                
                messages.success(
                    request, 
                    f'Empresa activa cambiada a: {empresa.razon_social}'
                )
                
            except Empresa.DoesNotExist:
                messages.error(request, 'No tienes acceso a esta empresa.')
        else:
            messages.error(request, 'Empresa no especificada.')
    
    return redirect('accounts:dashboard')
