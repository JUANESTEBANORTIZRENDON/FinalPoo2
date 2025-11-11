/**
 * Script para mostrar/ocultar campos dinámicamente en el formulario de PerfilUsuario
 * Controla la visibilidad de campos según el checkbox "crear_usuario_automaticamente"
 */

(function($) {
    'use strict';
    
    $(document).ready(function() {
        // Elementos del formulario
        const $checkboxCrearAuto = $('#id_crear_usuario_automaticamente');
        const $fieldsetUsuarioExistente = $('.field-usuario').closest('.form-row').parent();
        const $fieldsetDatosNuevoUsuario = $('[class*="field-username"]').closest('fieldset');
        
        // Función para mostrar/ocultar campos según el estado del checkbox
        function toggleFieldsVisibility() {
            const crearAutomaticamente = $checkboxCrearAuto.is(':checked');
            
            if (crearAutomaticamente) {
                // Mostrar campos de nuevo usuario
                $fieldsetDatosNuevoUsuario.show();
                
                // Ocultar y limpiar campo de usuario existente
                $fieldsetUsuarioExistente.hide();
                $('#id_usuario').val('').trigger('change');
                
                // Marcar campos de nuevo usuario como opcionales visualmente
                updateFieldLabels(true);
                
            } else {
                // Ocultar campos de nuevo usuario
                $fieldsetDatosNuevoUsuario.hide();
                
                // Mostrar campo de usuario existente
                $fieldsetUsuarioExistente.show();
                
                // Limpiar campos de nuevo usuario
                clearNewUserFields();
            }
        }
        
        // Función para limpiar campos de nuevo usuario
        function clearNewUserFields() {
            $('#id_username').val('');
            $('#id_first_name').val('');
            $('#id_last_name').val('');
            $('#id_email').val('');
            $('#id_password').val('');
        }
        
        // Función para actualizar labels de campos
        function updateFieldLabels(isAutoCreation) {
            const fields = ['username', 'first_name', 'last_name', 'email', 'password'];
            
            fields.forEach(function(fieldName) {
                const $label = $('label[for="id_' + fieldName + '"]');
                const originalText = $label.text().replace(' *', '').replace(' (opcional)', '');
                
                if (isAutoCreation) {
                    $label.text(originalText + ' (opcional)');
                } else {
                    $label.text(originalText);
                }
            });
        }
        
        // Inicializar estado al cargar la página
        if ($checkboxCrearAuto.length > 0) {
            // Configurar estado inicial
            toggleFieldsVisibility();
            
            // Escuchar cambios en el checkbox
            $checkboxCrearAuto.on('change', function() {
                toggleFieldsVisibility();
            });
            
            // Agregar animación suave
            $fieldsetDatosNuevoUsuario.css('transition', 'opacity 0.3s ease-in-out');
            $fieldsetUsuarioExistente.css('transition', 'opacity 0.3s ease-in-out');
        }
        
        // Mejorar UX: Expandir automáticamente el fieldset de Datos del Nuevo Usuario si está marcado
        if ($checkboxCrearAuto.is(':checked')) {
            const $collapseFieldset = $fieldsetDatosNuevoUsuario.find('.collapse');
            if ($collapseFieldset.length > 0) {
                $collapseFieldset.removeClass('collapse');
            }
        }
    });
    
})(django.jQuery);
