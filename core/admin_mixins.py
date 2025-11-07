"""
Mixins reutilizables para el admin de Django
"""
from django.contrib import admin


class EmpresaFilterMixin:
    """
    Mixin que filtra automáticamente los querysets por empresa activa
    
    Uso:
        class MiModelAdmin(EmpresaFilterMixin, admin.ModelAdmin):
            ...
    
    El modelo debe tener un campo 'empresa' (ForeignKey a Empresa)
    """
    
    def get_queryset(self, request):
        """
        Filtra el queryset por la empresa activa en la sesión del usuario
        """
        qs = super().get_queryset(request)
        
        # Obtener la empresa activa de la sesión
        empresa_id = request.session.get('empresa_activa_id')
        
        # Verificar si el modelo tiene el campo empresa
        if hasattr(qs.model, 'empresa') and empresa_id:
            # Filtrar por empresa
            return qs.filter(empresa_id=empresa_id)
        
        # Si no hay empresa activa o el modelo no tiene el campo, retornar el queryset completo
        return qs
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Filtra los ForeignKey relacionados con empresa
        """
        # Si el campo es 'empresa', filtrar por empresa activa
        if db_field.name == "empresa":
            empresa_id = request.session.get('empresa_activa_id')
            if empresa_id:
                from empresas.models import Empresa
                kwargs["queryset"] = Empresa.objects.filter(id=empresa_id)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ReadOnlyAdminMixin:
    """
    Mixin que hace que un ModelAdmin sea de solo lectura
    """
    
    def has_add_permission(self, request):  # noqa: ARG002
        """Deshabilita el permiso de agregar objetos"""
        return False
    
    def has_change_permission(self, request, obj=None):  # noqa: ARG002
        """Deshabilita el permiso de modificar objetos"""
        return False
    
    def has_delete_permission(self, request, obj=None):  # noqa: ARG002
        """Deshabilita el permiso de eliminar objetos"""
        return False


class ExportMixin:
    """
    Mixin que agrega funcionalidad de exportación CSV
    """
    
    def export_as_csv(self, request, queryset):
        """
        Exporta el queryset seleccionado como CSV
        """
        import csv
        from django.http import HttpResponse
        
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        
        writer = csv.writer(response)
        writer.writerow(field_names)
        
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        
        return response
    
    export_as_csv.short_description = "Exportar seleccionados como CSV"
    
    actions = ['export_as_csv']
