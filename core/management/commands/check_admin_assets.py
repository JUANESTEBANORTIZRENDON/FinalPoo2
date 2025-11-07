"""
Comando de management para verificar que los assets del admin están correctamente configurados.
Útil para debugging en producción y CI/CD.
"""

from django.core.management.base import BaseCommand
from django.contrib.staticfiles import finders
from django.conf import settings
from django.template.loader import get_template
import os


class Command(BaseCommand):
    help = 'Verifica que los assets personalizados del admin estén correctamente configurados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Muestra información detallada',
        )

    def handle(self, *args, **options):
        verbose = options['verbose']
        errors = []
        warnings = []
        
        self.stdout.write(self.style.SUCCESS('\n🔍 Verificando configuración de assets del admin...\n'))
        
        # Ejecutar verificaciones
        self._check_static_files(errors, verbose)
        self._check_static_settings(errors, warnings, verbose)
        self._check_storages(warnings)
        self._check_middleware(errors, warnings)
        self._check_templates(errors)
        self._check_template_config(warnings, verbose)
        
        # Mostrar resumen
        return self._print_summary(errors, warnings)
    
    def _check_static_files(self, errors, verbose):
        """Verifica archivos estáticos críticos"""
        critical_files = ['admin/css/admin_custom.css', 'admin/js/sidebar.js']
        self.stdout.write(self.style.HTTP_INFO('📁 Verificando archivos estáticos críticos:'))
        
        for file_path in critical_files:
            result = finders.find(file_path)
            if result:
                self.stdout.write(self.style.SUCCESS(f'   ✅ {file_path}'))
                if verbose:
                    paths = result if isinstance(result, list) else [result]
                    for path in paths:
                        self.stdout.write(f'      → {path}')
            else:
                errors.append(f'No se encuentra: {file_path}')
                self.stdout.write(self.style.ERROR(f'   ❌ {file_path} - NO ENCONTRADO'))
    
    def _check_static_settings(self, errors, warnings, verbose):
        """Verifica configuración de STATIC_*"""
        self.stdout.write(self.style.HTTP_INFO('\n⚙️  Verificando configuración STATIC:'))
        
        self._check_setting('STATIC_URL', errors, verbose=False)
        self._check_static_root(errors, verbose)
        self._check_staticfiles_dirs(warnings, verbose)
    
    def _check_setting(self, setting_name, errors, verbose=False, value_processor=None):
        """Verifica una configuración genérica"""
        value = getattr(settings, setting_name, None)
        if value:
            display_value = value_processor(value) if value_processor else value
            self.stdout.write(self.style.SUCCESS(f'   ✅ {setting_name} = {display_value}'))
            return True
        errors.append(f'{setting_name} no está configurado')
        self.stdout.write(self.style.ERROR(f'   ❌ {setting_name} no configurado'))
        return False
    
    def _check_static_root(self, errors, verbose):
        """Verifica STATIC_ROOT"""
        static_root = getattr(settings, 'STATIC_ROOT', None)
        if static_root:
            self.stdout.write(self.style.SUCCESS(f'   ✅ STATIC_ROOT = {static_root}'))
            if verbose and os.path.exists(static_root):
                file_count = sum(len(files) for r, d, files in os.walk(static_root))
                self.stdout.write(f'      → Contiene {file_count} archivos')
        else:
            errors.append('STATIC_ROOT no está configurado')
            self.stdout.write(self.style.ERROR('   ❌ STATIC_ROOT no configurado'))
    
    def _check_staticfiles_dirs(self, warnings, verbose):
        """Verifica STATICFILES_DIRS"""
        staticfiles_dirs = getattr(settings, 'STATICFILES_DIRS', [])
        if staticfiles_dirs:
            self.stdout.write(self.style.SUCCESS(
                f'   ✅ STATICFILES_DIRS configurado ({len(staticfiles_dirs)} directorios)'))
            if verbose:
                for directory in staticfiles_dirs:
                    self.stdout.write(f'      → {directory}')
        else:
            warnings.append('STATICFILES_DIRS está vacío')
            self.stdout.write(self.style.WARNING('   ⚠️  STATICFILES_DIRS está vacío'))
    
    def _check_storages(self, warnings):
        """Verifica configuración de STORAGES"""
        storages = getattr(settings, 'STORAGES', None)
        if storages and 'staticfiles' in storages:
            backend = storages['staticfiles']['BACKEND']
            self.stdout.write(self.style.SUCCESS(f'   ✅ STORAGES["staticfiles"] = {backend}'))
        else:
            warnings.append('STORAGES["staticfiles"] no está configurado (usando default)')
            self.stdout.write(self.style.WARNING('   ⚠️  STORAGES["staticfiles"] no configurado'))
    
    def _check_middleware(self, errors, warnings):
        """Verifica WhiteNoise en MIDDLEWARE"""
        self.stdout.write(self.style.HTTP_INFO('\n🔌 Verificando middleware:'))
        middleware = getattr(settings, 'MIDDLEWARE', [])
        
        whitenoise_idx = next((i for i, m in enumerate(middleware) if 'whitenoise' in m.lower()), None)
        security_idx = next((i for i, m in enumerate(middleware) if 'SecurityMiddleware' in m), None)
        
        if whitenoise_idx is None:
            errors.append('WhiteNoiseMiddleware no está en MIDDLEWARE')
            self.stdout.write(self.style.ERROR('   ❌ WhiteNoiseMiddleware no encontrado'))
        elif security_idx is not None and whitenoise_idx == security_idx + 1:
            self.stdout.write(self.style.SUCCESS('   ✅ WhiteNoiseMiddleware en posición correcta'))
        else:
            warnings.append('WhiteNoiseMiddleware debe ir justo después de SecurityMiddleware')
            self.stdout.write(self.style.WARNING(
                '   ⚠️  WhiteNoiseMiddleware no está justo después de SecurityMiddleware'))
    
    def _check_templates(self, errors):
        """Verifica templates del admin"""
        self.stdout.write(self.style.HTTP_INFO('\n📄 Verificando templates:'))
        try:
            template = get_template('admin/base_site.html')
            self.stdout.write(self.style.SUCCESS('   ✅ admin/base_site.html existe'))
            
            with open(template.origin.name, 'r', encoding='utf-8') as f:
                content = f.read()
                self._check_template_content(content, errors)
        except Exception as e:
            errors.append(f'Error al cargar admin/base_site.html: {str(e)}')
            self.stdout.write(self.style.ERROR(f'   ❌ Error: {str(e)}'))
    
    def _check_template_content(self, content, errors):
        """Verifica el contenido del template"""
        checks = [
            ('{% load static %}', 'Template usa {% load static %}', 
             'admin/base_site.html no carga {% load static %}'),
            ('admin_custom.css', 'Template referencia admin_custom.css',
             'admin/base_site.html no referencia admin_custom.css'),
            ('sidebar.js', 'Template referencia sidebar.js',
             'admin/base_site.html no referencia sidebar.js'),
        ]
        
        for search_str, success_msg, error_msg in checks:
            if search_str in content:
                self.stdout.write(self.style.SUCCESS(f'   ✅ {success_msg}'))
            else:
                errors.append(error_msg)
                self.stdout.write(self.style.ERROR(f'   ❌ {success_msg.replace("usa", "NO usa")}'))
    
    def _check_template_config(self, warnings, verbose):
        """Verifica configuración de TEMPLATES"""
        self.stdout.write(self.style.HTTP_INFO('\n🗂️  Verificando configuración TEMPLATES:'))
        templates = getattr(settings, 'TEMPLATES', [])
        
        if not templates:
            return
        
        template_dirs = templates[0].get('DIRS', [])
        if template_dirs:
            self.stdout.write(self.style.SUCCESS(
                f'   ✅ TEMPLATES[0]["DIRS"] configurado ({len(template_dirs)} directorios)'))
            if verbose:
                for directory in template_dirs:
                    self.stdout.write(f'      → {directory}')
        else:
            warnings.append('TEMPLATES[0]["DIRS"] está vacío')
            self.stdout.write(self.style.WARNING('   ⚠️  TEMPLATES[0]["DIRS"] está vacío'))
        
        app_dirs = templates[0].get('APP_DIRS', False)
        if app_dirs:
            self.stdout.write(self.style.SUCCESS('   ✅ APP_DIRS = True'))
        else:
            warnings.append('APP_DIRS = False (puede causar problemas)')
            self.stdout.write(self.style.WARNING('   ⚠️  APP_DIRS = False'))
    
    def _print_summary(self, errors, warnings):
        """Imprime resumen final y retorna código de salida"""
        self.stdout.write('\n' + '='*70)
        
        if errors:
            self.stdout.write(self.style.ERROR(f'\n❌ ERRORES ENCONTRADOS ({len(errors)}):'))
            for error in errors:
                self.stdout.write(self.style.ERROR(f'   • {error}'))
        
        if warnings:
            self.stdout.write(self.style.WARNING(f'\n⚠️  ADVERTENCIAS ({len(warnings)}):'))
            for warning in warnings:
                self.stdout.write(self.style.WARNING(f'   • {warning}'))
        
        if not errors and not warnings:
            self.stdout.write(self.style.SUCCESS(
                '\n✨ ¡TODO ESTÁ CORRECTO! Los assets del admin deberían funcionar.\n'))
            return 0
        if not errors:
            self.stdout.write(self.style.SUCCESS(
                '\n✅ No hay errores críticos, pero revisa las advertencias.\n'))
            return 0
        
        self.stdout.write(self.style.ERROR('\n❌ Hay errores que deben corregirse.\n'))
        return 1
