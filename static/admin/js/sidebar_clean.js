/**
 * Limpieza agresiva del sidebar del panel de desarrollador
 * Elimina todos los elementos que no sean etiquetas de aplicación
 * @version 2024-11-06
 */

(function() {
    'use strict';

    console.log('🚀 Iniciando limpieza del sidebar del admin...');

    function limpiarSidebar() {
        const sidebar = document.getElementById('nav-sidebar');
        
        if (!sidebar) {
            console.warn('⚠️ No se encontró el sidebar (#nav-sidebar)');
            return;
        }

        console.log('✅ Sidebar encontrado, iniciando limpieza...');
        
        // Paso 1: Ocultar todas las listas de modelos
        const listas = sidebar.querySelectorAll('.model-list, ul, li');
        console.log(`📋 Encontradas ${listas.length} listas/items a ocultar`);
        listas.forEach(function(lista) {
            lista.style.display = 'none';
            lista.style.visibility = 'hidden';
            lista.style.height = '0';
            lista.style.overflow = 'hidden';
        });

        // Paso 2: Ocultar todos los enlaces que NO son app-label
        const enlaces = sidebar.querySelectorAll('a:not(.app-label)');
        console.log(`🔗 Encontrados ${enlaces.length} enlaces no-app-label a ocultar`);
        enlaces.forEach(function(enlace) {
            enlace.style.display = 'none';
            enlace.style.visibility = 'hidden';
        });

        // Paso 3: Ocultar botones "Añadir" y otros elementos
        const botones = sidebar.querySelectorAll('.addlink, .changelink, .deletelink, [class*="add-"], [class*="change-"], [class*="delete-"]');
        console.log(`🔘 Encontrados ${botones.length} botones a ocultar`);
        botones.forEach(function(boton) {
            boton.style.display = 'none';
            boton.style.visibility = 'hidden';
        });

        // Paso 4: Asegurar que las app-label sean visibles
        const appLabels = sidebar.querySelectorAll('.app-label');
        console.log(`📱 Encontradas ${appLabels.length} app-labels - asegurando visibilidad`);
        appLabels.forEach(function(label) {
            label.style.display = 'block';
            label.style.visibility = 'visible';
            
            // Agregar manejador de click si no lo tiene
            if (!label.hasAttribute('data-click-handler')) {
                label.setAttribute('data-click-handler', 'true');
                label.style.cursor = 'pointer';
                
                label.addEventListener('click', function(e) {
                    e.preventDefault();
                    const appName = this.textContent.trim().toLowerCase();
                    console.log(`🖱️ Click en app: ${appName}`);
                    
                    // Mapeo de nombres de apps a URLs
                    const urls = {
                        'empresas': '/empresas/admin/holdings/',
                        'cuentas': '/admin/accounts/',
                        'api': '/admin/api/',
                        'catalogos': '/catalogos/',
                        'catálogos': '/catalogos/',
                        'facturación': '/facturacion/',
                        'facturacion': '/facturacion/',
                        'tesorería': '/tesoreria/',
                        'tesoreria': '/tesoreria/',
                        'contabilidad': '/contabilidad/',
                        'reportes': '/reportes/',
                        'ventas': '/ventas/'
                    };
                    
                    const url = urls[appName];
                    if (url) {
                        console.log(`🔄 Redirigiendo a: ${url}`);
                        window.location.href = url;
                    } else {
                        console.warn(`⚠️ No se encontró URL para: ${appName}`);
                    }
                });
            }
        });

        console.log('✨ Limpieza del sidebar completada');
    }

    // Ejecutar múltiples veces para asegurar que se aplique
    // 1. Cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', limpiarSidebar);
    } else {
        limpiarSidebar();
    }

    // 2. Después de un pequeño delay (por si hay carga asíncrona)
    setTimeout(limpiarSidebar, 100);

    // 3. Después de un delay mayor (para asegurar)
    setTimeout(limpiarSidebar, 500);

    console.log('🎯 Script de limpieza del sidebar cargado');
})();
