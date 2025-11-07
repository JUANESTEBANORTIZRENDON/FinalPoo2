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
        
        # 1. Verificar archivos estáticos críticos
        critical_files = [
            'admin/css/admin_custom.css',
            'admin/js/sidebar.js',
        ]
        
        self.stdout.write(self.style.HTTP_INFO('📁 Verificando archivos estáticos críticos:'))
        for file_path in critical_files:
            result = finders.find(file_path)
            if result:
                self.stdout.write(self.style.SUCCESS(f'   ✅ {file_path}'))
                if verbose:
                    if isinstance(result, list):
                        for path in result:
                            self.stdout.write(f'      → {path}')
                    else:
                        self.stdout.write(f'      → {result}')
            else:
                errors.append(f'No se encuentra: {file_path}')
                self.stdout.write(self.style.ERROR(f'   ❌ {file_path} - NO ENCONTRADO'))
        
        # 2. Verificar configuración de STATIC_*
        self.stdout.write(self.style.HTTP_INFO('\n⚙️  Verificando configuración STATIC:'))
        
        static_url = getattr(settings, 'STATIC_URL', None)
        if static_url:
            self.stdout.write(self.style.SUCCESS(f'   ✅ STATIC_URL = {static_url}'))
        else:
            errors.append('STATIC_URL no está configurado')
            self.stdout.write(self.style.ERROR('   ❌ STATIC_URL no configurado'))
        
        static_root = getattr(settings, 'STATIC_ROOT', None)
        if static_root:
            self.stdout.write(self.style.SUCCESS(f'   ✅ STATIC_ROOT = {static_root}'))
            if verbose and os.path.exists(static_root):
                file_count = sum([len(files) for r, d, files in os.walk(static_root)])
                self.stdout.write(f'      → Contiene {file_count} archivos')
        else:
            errors.append('STATIC_ROOT no está configurado')
            self.stdout.write(self.style.ERROR('   ❌ STATIC_ROOT no configurado'))
        
        staticfiles_dirs = getattr(settings, 'STATICFILES_DIRS', [])
        if staticfiles_dirs:
            self.stdout.write(self.style.SUCCESS(f'   ✅ STATICFILES_DIRS configurado ({len(staticfiles_dirs)} directorios)'))
            if verbose:
                for d in staticfiles_dirs:
                    self.stdout.write(f'      → {d}')
        else:
            warnings.append('STATICFILES_DIRS está vacío')
            self.stdout.write(self.style.WARNING('   ⚠️  STATICFILES_DIRS está vacío'))
        
        # 3. Verificar STORAGES
        storages = getattr(settings, 'STORAGES', None)
        if storages and 'staticfiles' in storages:
            backend = storages['staticfiles']['BACKEND']
            self.stdout.write(self.style.SUCCESS(f'   ✅ STORAGES["staticfiles"] = {backend}'))
        else:
            warnings.append('STORAGES["staticfiles"] no está configurado (usando default)')
            self.stdout.write(self.style.WARNING('   ⚠️  STORAGES["staticfiles"] no configurado'))
        
        # 4. Verificar WhiteNoise en MIDDLEWARE
        self.stdout.write(self.style.HTTP_INFO('\n🔌 Verificando middleware:'))
        middleware = getattr(settings, 'MIDDLEWARE', [])
        whitenoise_idx = next((i for i, m in enumerate(middleware) if 'whitenoise' in m.lower()), None)
        security_idx = next((i for i, m in enumerate(middleware) if 'SecurityMiddleware' in m), None)
        
        if whitenoise_idx is not None:
            if security_idx is not None and whitenoise_idx == security_idx + 1:
                self.stdout.write(self.style.SUCCESS('   ✅ WhiteNoiseMiddleware en posición correcta'))
            else:
                warnings.append('WhiteNoiseMiddleware debe ir justo después de SecurityMiddleware')
                self.stdout.write(self.style.WARNING('   ⚠️  WhiteNoiseMiddleware no está justo después de SecurityMiddleware'))
        else:
            errors.append('WhiteNoiseMiddleware no está en MIDDLEWARE')
            self.stdout.write(self.style.ERROR('   ❌ WhiteNoiseMiddleware no encontrado'))
        
        # 5. Verificar templates
        self.stdout.write(self.style.HTTP_INFO('\n📄 Verificando templates:'))
        try:
            template = get_template('admin/base_site.html')
            self.stdout.write(self.style.SUCCESS('   ✅ admin/base_site.html existe'))
            
            # Verificar que carga static
            with open(template.origin.name, 'r', encoding='utf-8') as f:
                content = f.read()
                if '{% load static %}' in content:
                    self.stdout.write(self.style.SUCCESS('   ✅ Template usa {% load static %}'))
                else:
                    errors.append('admin/base_site.html no carga {% load static %}')
                    self.stdout.write(self.style.ERROR('   ❌ Template NO usa {% load static %}'))
                
                if 'admin_custom.css' in content:
                    self.stdout.write(self.style.SUCCESS('   ✅ Template referencia admin_custom.css'))
                else:
                    errors.append('admin/base_site.html no referencia admin_custom.css')
                    self.stdout.write(self.style.ERROR('   ❌ Template NO referencia admin_custom.css'))
                
                if 'sidebar.js' in content:
                    self.stdout.write(self.style.SUCCESS('   ✅ Template referencia sidebar.js'))
                else:
                    errors.append('admin/base_site.html no referencia sidebar.js')
                    self.stdout.write(self.style.ERROR('   ❌ Template NO referencia sidebar.js'))
                    
        except Exception as e:
            errors.append(f'Error al cargar admin/base_site.html: {str(e)}')
            self.stdout.write(self.style.ERROR(f'   ❌ Error: {str(e)}'))
        
        # 6. Verificar TEMPLATES
        self.stdout.write(self.style.HTTP_INFO('\n🗂️  Verificando configuración TEMPLATES:'))
        templates = getattr(settings, 'TEMPLATES', [])
        if templates:
            template_dirs = templates[0].get('DIRS', [])
            if template_dirs:
                self.stdout.write(self.style.SUCCESS(f'   ✅ TEMPLATES[0]["DIRS"] configurado ({len(template_dirs)} directorios)'))
                if verbose:
                    for d in template_dirs:
                        self.stdout.write(f'      → {d}')
            else:
                warnings.append('TEMPLATES[0]["DIRS"] está vacío')
                self.stdout.write(self.style.WARNING('   ⚠️  TEMPLATES[0]["DIRS"] está vacío'))
            
            app_dirs = templates[0].get('APP_DIRS', False)
            if app_dirs:
                self.stdout.write(self.style.SUCCESS('   ✅ APP_DIRS = True'))
            else:
                warnings.append('APP_DIRS = False (puede causar problemas)')
                self.stdout.write(self.style.WARNING('   ⚠️  APP_DIRS = False'))
        
        # Resumen final
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
            self.stdout.write(self.style.SUCCESS('\n✨ ¡TODO ESTÁ CORRECTO! Los assets del admin deberían funcionar.\n'))
            return 0
        elif not errors:
            self.stdout.write(self.style.SUCCESS('\n✅ No hay errores críticos, pero revisa las advertencias.\n'))
            return 0
        else:
            self.stdout.write(self.style.ERROR('\n❌ Hay errores que deben corregirse.\n'))
            return 1
