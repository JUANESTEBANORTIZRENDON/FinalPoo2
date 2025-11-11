/**
 * Script para habilitar/deshabilitar campos dinámicamente en el formulario de PerfilUsuario
 * Controla la habilitación de campos según el checkbox "crear_usuario_automaticamente"
 */

(function($) {
    'use strict';
    
    $(document).ready(function() {
        console.log('🚀 Perfil Usuario Inteligente - Script cargado');
        
        // Esperar a que el DOM esté completamente cargado
        setTimeout(function() {
            initializeToggle();
        }, 100);
    });
    
    function initializeToggle() {
        // Elementos del formulario
        const $checkboxCrearAuto = $('#id_crear_usuario_automaticamente');
        
        if ($checkboxCrearAuto.length === 0) {
            console.warn('⚠️ Checkbox crear_usuario_automaticamente no encontrado');
            return;
        }
        
        console.log('✅ Checkbox encontrado, estado inicial:', $checkboxCrearAuto.is(':checked'));
        
        // Campos de nuevo usuario que se van a habilitar/deshabilitar
        const camposNuevoUsuario = [
            '#id_username',
            '#id_first_name', 
            '#id_last_name',
            '#id_email',
            '#id_password',
            '#id_is_active'
        ];
        
        // Campo de usuario existente
        const $campoUsuario = $('#id_usuario');
        
        // Función para habilitar/deshabilitar campos según el estado del checkbox
        function toggleFieldsState() {
            const crearAutomaticamente = $checkboxCrearAuto.is(':checked');
            console.log('🔄 Toggle - Crear automáticamente:', crearAutomaticamente);
            
            if (crearAutomaticamente) {
                // Habilitar campos de nuevo usuario
                camposNuevoUsuario.forEach(function(selector) {
                    const $campo = $(selector);
                    if ($campo.length > 0) {
                        $campo.prop('disabled', false)
                              .css({
                                  'opacity': '1',
                                  'background-color': '',
                                  'cursor': 'text'
                              });
                        
                        // Remover atributo readonly si existe
                        $campo.removeAttr('readonly');
                    }
                });
                console.log('✅ Campos de nuevo usuario HABILITADOS');
                
                // Deshabilitar y limpiar campo de usuario existente
                if ($campoUsuario.length > 0) {
                    $campoUsuario.prop('disabled', true)
                                 .val('')
                                 .css({
                                     'opacity': '0.5',
                                     'background-color': '#f5f5f5',
                                     'cursor': 'not-allowed'
                                 });
                    console.log('� Campo Usuario Existente DESHABILITADO');
                }
                
            } else {
                // Deshabilitar y limpiar campos de nuevo usuario
                camposNuevoUsuario.forEach(function(selector) {
                    const $campo = $(selector);
                    if ($campo.length > 0) {
                        $campo.prop('disabled', true)
                              .val('')
                              .css({
                                  'opacity': '0.5',
                                  'background-color': '#f5f5f5',
                                  'cursor': 'not-allowed'
                              });
                        
                        // Para checkbox is_active, desmarcarlo
                        if (selector === '#id_is_active') {
                            $campo.prop('checked', false);
                        }
                    }
                });
                console.log('� Campos de nuevo usuario DESHABILITADOS y limpiados');
                
                // Habilitar campo de usuario existente
                if ($campoUsuario.length > 0) {
                    $campoUsuario.prop('disabled', false)
                                 .css({
                                     'opacity': '1',
                                     'background-color': '',
                                     'cursor': 'pointer'
                                 });
                    console.log('✅ Campo Usuario Existente HABILITADO');
                }
            }
        }
        
        // Configurar estado inicial
        toggleFieldsState();
        
        // Escuchar cambios en el checkbox
        $checkboxCrearAuto.on('change', function() {
            console.log('📝 Checkbox cambiado a:', $(this).is(':checked'));
            toggleFieldsState();
        });
        
        // Prevenir edición de campos deshabilitados (seguridad adicional)
        camposNuevoUsuario.forEach(function(selector) {
            $(selector).on('focus', function() {
                if ($(this).prop('disabled')) {
                    $(this).blur();
                    console.log('⚠️ Intento de editar campo deshabilitado bloqueado');
                }
            });
        });
        
        console.log('✅ Script configurado correctamente - Modo habilitar/deshabilitar');
    }
    
})(django.jQuery);
