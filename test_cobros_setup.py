"""
Script de verificación de la implementación de cobros.
Verifica que todos los archivos y configuraciones estén correctos.
"""

import os
import sys

def verificar_archivos():
    """Verifica que todos los archivos necesarios existan"""
    archivos_requeridos = [
        'tesoreria/views.py',
        'tesoreria/urls.py',
        'tesoreria/forms.py',
        'tesoreria/models.py',
        'templates/tesoreria/cobros_lista.html',
        'templates/tesoreria/cobros_crear.html',
        'templates/tesoreria/cobros_editar.html',
        'templates/tesoreria/cobros_eliminar.html',
        'requirements.txt',
    ]
    
    print("🔍 Verificando archivos...")
    todos_existen = True
    
    for archivo in archivos_requeridos:
        ruta_completa = os.path.join(os.path.dirname(__file__), archivo)
        if os.path.exists(ruta_completa):
            print(f"  ✅ {archivo}")
        else:
            print(f"  ❌ {archivo} - NO ENCONTRADO")
            todos_existen = False
    
    return todos_existen

def verificar_dependencias():
    """Verifica que las dependencias estén en requirements.txt"""
    print("\n📦 Verificando dependencias en requirements.txt...")
    
    ruta_requirements = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    
    if not os.path.exists(ruta_requirements):
        print("  ❌ requirements.txt no encontrado")
        return False
    
    with open(ruta_requirements, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    dependencias_requeridas = ['reportlab', 'weasyprint']
    todas_presentes = True
    
    for dep in dependencias_requeridas:
        if dep in contenido:
            print(f"  ✅ {dep}")
        else:
            print(f"  ❌ {dep} - NO ENCONTRADA")
            todas_presentes = False
    
    return todas_presentes

def verificar_urls():
    """Verifica que las URLs estén configuradas"""
    print("\n🔗 Verificando configuración de URLs...")
    
    ruta_urls = os.path.join(os.path.dirname(__file__), 'tesoreria', 'urls.py')
    
    if not os.path.exists(ruta_urls):
        print("  ❌ tesoreria/urls.py no encontrado")
        return False
    
    with open(ruta_urls, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    urls_requeridas = [
        'cobros_editar',
        'cobros_eliminar',
        'cobros_activar',
        'factura_pdf',
    ]
    
    todas_presentes = True
    
    for url in urls_requeridas:
        if url in contenido:
            print(f"  ✅ {url}")
        else:
            print(f"  ❌ {url} - NO ENCONTRADA")
            todas_presentes = False
    
    return todas_presentes

def verificar_vistas():
    """Verifica que las vistas estén implementadas"""
    print("\n👁️ Verificando vistas en views.py...")
    
    ruta_views = os.path.join(os.path.dirname(__file__), 'tesoreria', 'views.py')
    
    if not os.path.exists(ruta_views):
        print("  ❌ tesoreria/views.py no encontrado")
        return False
    
    with open(ruta_views, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    vistas_requeridas = [
        'CobroUpdateView',
        'CobroDeleteView',
        'activar_cobro',
        'generar_factura_pdf',
    ]
    
    todas_presentes = True
    
    for vista in vistas_requeridas:
        if vista in contenido:
            print(f"  ✅ {vista}")
        else:
            print(f"  ❌ {vista} - NO ENCONTRADA")
            todas_presentes = False
    
    return todas_presentes

def main():
    """Función principal"""
    print("=" * 60)
    print("🚀 VERIFICACIÓN DE IMPLEMENTACIÓN DE COBROS")
    print("=" * 60)
    
    resultados = []
    
    resultados.append(verificar_archivos())
    resultados.append(verificar_dependencias())
    resultados.append(verificar_urls())
    resultados.append(verificar_vistas())
    
    print("\n" + "=" * 60)
    if all(resultados):
        print("✅ TODAS LAS VERIFICACIONES PASARON")
        print("=" * 60)
        print("\n📝 Próximos pasos:")
        print("  1. Ejecutar: pip install -r requirements.txt")
        print("  2. Ejecutar: python manage.py makemigrations")
        print("  3. Ejecutar: python manage.py migrate")
        print("  4. Ejecutar: python manage.py runserver")
        print("  5. Probar la funcionalidad en: http://localhost:8000/tesoreria/cobros/")
        return 0
    else:
        print("❌ ALGUNAS VERIFICACIONES FALLARON")
        print("=" * 60)
        print("\n⚠️ Por favor, revisa los errores anteriores.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
