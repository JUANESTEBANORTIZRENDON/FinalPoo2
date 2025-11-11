/**
 * Script para mostrar/ocultar campos dinámicamente en el formulario de PerfilUsuario
 * Controla la visibilidad de campos según el checkbox "crear_usuario_automaticamente"
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
        
        // Encontrar fieldsets - buscar por clase collapsed o por título
        let $fieldsetUsuarioExistente = null;
        let $fieldsetDatosNuevoUsuario = null;
        
        // Buscar el fieldset que contiene el campo 'usuario'
        const $campoUsuario = $('.field-usuario');
        if ($campoUsuario.length > 0) {
            $fieldsetUsuarioExistente = $campoUsuario.closest('fieldset');
            console.log('✅ Fieldset Usuario Existente encontrado por campo');
        }
        
        // Buscar el fieldset que contiene los campos de nuevo usuario
        const $campoUsername = $('.field-username');
        if ($campoUsername.length > 0) {
            $fieldsetDatosNuevoUsuario = $campoUsername.closest('fieldset');
            console.log('✅ Fieldset Datos del Nuevo Usuario encontrado por campo');
        }
        
        // Si no se encontró, buscar por título del fieldset
        if (!$fieldsetUsuarioExistente || !$fieldsetDatosNuevoUsuario) {
            $('fieldset.module').each(function() {
                const $fieldset = $(this);
                const $h2 = $fieldset.find('h2');
                const titulo = $h2.text().trim();
                
                if ((titulo.includes('Usuario Existente') || titulo.includes('👤')) && !$fieldsetUsuarioExistente) {
                    $fieldsetUsuarioExistente = $fieldset;
                    console.log('✅ Fieldset Usuario Existente encontrado por título');
                }
                
                if ((titulo.includes('Datos del Nuevo Usuario') || titulo.includes('🔐')) && !$fieldsetDatosNuevoUsuario) {
                    $fieldsetDatosNuevoUsuario = $fieldset;
                    console.log('✅ Fieldset Datos del Nuevo Usuario encontrado por título');
                }
            });
        }
        
        if (!$fieldsetUsuarioExistente || !$fieldsetDatosNuevoUsuario) {
            console.error('❌ No se encontraron los fieldsets necesarios');
            console.log('Usuario Existente:', $fieldsetUsuarioExistente);
            console.log('Datos Nuevo Usuario:', $fieldsetDatosNuevoUsuario);
            return;
        }
        
        // Función para mostrar/ocultar campos según el estado del checkbox
        function toggleFieldsVisibility() {
            const crearAutomaticamente = $checkboxCrearAuto.is(':checked');
            console.log('🔄 Toggle - Crear automáticamente:', crearAutomaticamente);
            
            if (crearAutomaticamente) {
                // Mostrar campos de nuevo usuario
                $fieldsetDatosNuevoUsuario.removeClass('collapsed').show();
                console.log('👁️ Mostrando Datos del Nuevo Usuario');
                
                // Ocultar campo de usuario existente
                $fieldsetUsuarioExistente.addClass('collapsed').hide();
                $('#id_usuario').val('');
                console.log('🙈 Ocultando Usuario Existente');
                
            } else {
                // Ocultar campos de nuevo usuario - IMPORTANTE: usar hide() para ocultarlo completamente
                $fieldsetDatosNuevoUsuario.addClass('collapsed').hide();
                console.log('🙈 Ocultando Datos del Nuevo Usuario');
                
                // Mostrar campo de usuario existente
                $fieldsetUsuarioExistente.removeClass('collapsed').show();
                console.log('👁️ Mostrando Usuario Existente');
                
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
            console.log('📝 Checkbox cambiado a:', $(this).is(':checked'));
            toggleFieldsVisibility();
        });
        
        console.log('✅ Script configurado correctamente');
    }
    
})(django.jQuery);
