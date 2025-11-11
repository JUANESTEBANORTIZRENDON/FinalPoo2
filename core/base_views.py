"""
Vistas base reutilizables para reducir duplicación de código
Compatibles con Django 5.x
"""
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from empresas.middleware import EmpresaFilterMixin


class BaseListView(LoginRequiredMixin, EmpresaFilterMixin, ListView):
    """Vista base para listar objetos con autenticación y filtro por empresa"""
    paginate_by = 50
    
    def get_queryset(self):
        """Aplicar filtros básicos de empresa"""
        queryset = super().get_queryset()
        return queryset.order_by('-created_at') if hasattr(queryset.model, 'created_at') else queryset


class BaseDetailView(LoginRequiredMixin, EmpresaFilterMixin, DetailView):
    """Vista base para detalles con autenticación y filtro por empresa"""
    pass


class BaseCreateView(LoginRequiredMixin, EmpresaFilterMixin, CreateView):
    """Vista base para crear objetos con autenticación y filtro por empresa"""
    
    def form_valid(self, form):
        """Asignar empresa activa automáticamente si el modelo tiene el campo"""
        if hasattr(form.instance, 'empresa'):
            form.instance.empresa = getattr(self.request, 'empresa_activa', None)
        
        response = super().form_valid(form)
        
        # Mensaje de éxito automático
        model_name = self.model._meta.verbose_name or 'Objeto'
        messages.success(
            self.request,
            f'{str(model_name).capitalize()} creado exitosamente.'
        )
        return response


class BaseUpdateView(LoginRequiredMixin, EmpresaFilterMixin, UpdateView):
    """Vista base para actualizar objetos con autenticación y filtro por empresa"""
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Mensaje de éxito automático
        model_name = self.model._meta.verbose_name or 'Objeto'
        messages.success(
            self.request,
            f'{str(model_name).capitalize()} actualizado exitosamente.'
        )
        return response


class BaseDeleteView(LoginRequiredMixin, EmpresaFilterMixin, DeleteView):
    """Vista base para eliminar objetos con autenticación y filtro por empresa"""
    
    def delete(self, request, *args, **kwargs):
        model_name = self.model._meta.verbose_name or 'Objeto'
        
        response = super().delete(request, *args, **kwargs)
        
        messages.success(
            request,
            f'{str(model_name).capitalize()} eliminado exitosamente.'
        )
        return response


class BaseIndexView(LoginRequiredMixin, TemplateView):
    """Vista base para páginas de índice/inicio de módulos"""
    pass


# Vistas simples sin filtro de empresa (para casos especiales)
class SimpleListView(LoginRequiredMixin, ListView):
    """Vista de lista sin filtro de empresa"""
    paginate_by = 50


class SimpleDetailView(LoginRequiredMixin, DetailView):
    """Vista de detalle sin filtro de empresa"""
    pass


class SimpleCreateView(LoginRequiredMixin, CreateView):
    """Vista de creación sin filtro de empresa"""
    
    def form_valid(self, form):
        response = super().form_valid(form)
        model_name = self.model._meta.verbose_name or 'Objeto'
        messages.success(
            self.request,
            f'{str(model_name).capitalize()} creado exitosamente.'
        )
        return response


class SimpleUpdateView(LoginRequiredMixin, UpdateView):
    """Vista de actualización sin filtro de empresa"""
    
    def form_valid(self, form):
        response = super().form_valid(form)
        model_name = self.model._meta.verbose_name or 'Objeto'
        messages.success(
            self.request,
            f'{str(model_name).capitalize()} actualizado exitosamente.'
        )
        return response


class SimpleDeleteView(LoginRequiredMixin, DeleteView):
    """Vista de eliminación sin filtro de empresa"""
    
    def delete(self, request, *args, **kwargs):
        model_name = self.model._meta.verbose_name or 'Objeto'
        
        response = super().delete(request, *args, **kwargs)
        
        messages.success(
            request,
            f'{str(model_name).capitalize()} eliminado exitosamente.'
        )
        return response
