/**
 * Script para mostrar/ocultar campos dinámicamente en el formulario de PerfilUsuario
 * Controla la visibilidad de campos según el checkbox "crear_usuario_automaticamente"
 */

(function($) {
    'use strict';
    
    $(document).ready(function() {
        console.log('🚀 Perfil Usuario Inteligente - Script cargado');
        
        // Elementos del formulario
        const $checkboxCrearAuto = $('#id_crear_usuario_automaticamente');
        
        if ($checkboxCrearAuto.length === 0) {
            console.warn('⚠️ Checkbox crear_usuario_automaticamente no encontrado');
            return;
        }
        
        console.log('✅ Checkbox encontrado, estado inicial:', $checkboxCrearAuto.is(':checked'));
        
        // Encontrar fieldsets por el contenido del título
        const $allFieldsets = $('fieldset.module');
        let $fieldsetUsuarioExistente = null;
        let $fieldsetDatosNuevoUsuario = null;
        
        // Buscar fieldsets por su título
        $allFieldsets.each(function() {
            const $fieldset = $(this);
            const $h2 = $fieldset.find('h2');
            const titulo = $h2.text().trim();
            
            if (titulo.includes('Usuario Existente') || titulo.includes('👤')) {
                $fieldsetUsuarioExistente = $fieldset;
                console.log('✅ Fieldset Usuario Existente encontrado');
            }
            
            if (titulo.includes('Datos del Nuevo Usuario') || titulo.includes('🔐')) {
                $fieldsetDatosNuevoUsuario = $fieldset;
                console.log('✅ Fieldset Datos del Nuevo Usuario encontrado');
            }
        });
        
        // Función para mostrar/ocultar campos según el estado del checkbox
        function toggleFieldsVisibility() {
            const crearAutomaticamente = $checkboxCrearAuto.is(':checked');
            console.log('🔄 Toggle - Crear automáticamente:', crearAutomaticamente);
            
            if (crearAutomaticamente) {
                // Mostrar campos de nuevo usuario
                if ($fieldsetDatosNuevoUsuario) {
                    $fieldsetDatosNuevoUsuario.show().css('opacity', '1');
                    console.log('👁️ Mostrando Datos del Nuevo Usuario');
                }
                
                // Ocultar campo de usuario existente
                if ($fieldsetUsuarioExistente) {
                    $fieldsetUsuarioExistente.hide().css('opacity', '0');
                    $('#id_usuario').val('').trigger('change');
                    console.log('🙈 Ocultando Usuario Existente');
                }
                
            } else {
                // Ocultar campos de nuevo usuario
                if ($fieldsetDatosNuevoUsuario) {
                    $fieldsetDatosNuevoUsuario.hide().css('opacity', '0');
                    console.log('🙈 Ocultando Datos del Nuevo Usuario');
                }
                
                // Mostrar campo de usuario existente
                if ($fieldsetUsuarioExistente) {
                    $fieldsetUsuarioExistente.show().css('opacity', '1');
                    console.log('👁️ Mostrando Usuario Existente');
                }
                
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
            $('#id_is_active').prop('checked', true);
            console.log('🧹 Campos de nuevo usuario limpiados');
        }
        
        // Configurar estado inicial
        toggleFieldsVisibility();
        
        // Escuchar cambios en el checkbox
        $checkboxCrearAuto.on('change', function() {
            console.log('📝 Checkbox cambiado');
            toggleFieldsVisibility();
        });
        
        // Agregar estilos de transición
        if ($fieldsetDatosNuevoUsuario) {
            $fieldsetDatosNuevoUsuario.css('transition', 'opacity 0.3s ease-in-out');
        }
        if ($fieldsetUsuarioExistente) {
            $fieldsetUsuarioExistente.css('transition', 'opacity 0.3s ease-in-out');
        }
        
        console.log('✅ Script configurado correctamente');
    });
    
})(django.jQuery);
