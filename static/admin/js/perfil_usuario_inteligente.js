/**
 * Script para habilitar/deshabilitar campos dinámicamente en el formulario de PerfilUsuario
 * Controla la habilitación de campos según el checkbox "crear_usuario_automaticamente"
 * Usa JavaScript vanilla para máxima compatibilidad
 */

(function() {
    'use strict';
    
    console.log('📦 Perfil Usuario Inteligente - Módulo cargado');
    
    // Esperar a que el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    function init() {
        console.log('🚀 DOM Ready - Inicializando controles');
        
        // Usar setTimeout para asegurar que todos los campos estén renderizados
        setTimeout(function() {
            initializeToggle();
        }, 300);
    }
    
    function initializeToggle() {
        console.log('🔧 Iniciando initializeToggle...');
        
        // Elementos del formulario
        var checkboxCrearAuto = document.getElementById('id_crear_usuario_automaticamente');
        
        if (!checkboxCrearAuto) {
            console.error('❌ Checkbox crear_usuario_automaticamente NO encontrado');
            return;
        }
        
        console.log('✅ Checkbox encontrado, estado inicial:', checkboxCrearAuto.checked);
        
        // IDs de campos de nuevo usuario que se van a habilitar/deshabilitar
        var camposNuevoUsuario = [
            'id_username',
            'id_first_name', 
            'id_last_name',
            'id_email',
            'id_password',
            'id_is_active'
        ];
        
        // Campo de usuario existente
        var campoUsuario = document.getElementById('id_usuario');
        
        // Función para habilitar/deshabilitar campos según el estado del checkbox
        function toggleFieldsState() {
            var crearAutomaticamente = checkboxCrearAuto.checked;
            console.log('🔄 Toggle ejecutado - Crear automáticamente:', crearAutomaticamente);
            
            if (crearAutomaticamente) {
                // Habilitar campos de nuevo usuario
                console.log('📝 Habilitando campos de nuevo usuario...');
                camposNuevoUsuario.forEach(function(fieldId) {
                    var campo = document.getElementById(fieldId);
                    if (campo) {
                        campo.disabled = false;
                        campo.readOnly = false;
                        campo.style.opacity = '1';
                        campo.style.backgroundColor = '';
                        campo.style.cursor = 'text';
                        console.log('  ✓ Campo habilitado:', fieldId);
                    } else {
                        console.warn('  ⚠️ Campo no encontrado:', fieldId);
                    }
                });
                
                // Deshabilitar y limpiar campo de usuario existente
                if (campoUsuario) {
                    campoUsuario.disabled = true;
                    campoUsuario.value = '';
                    campoUsuario.style.opacity = '0.5';
                    campoUsuario.style.backgroundColor = '#f5f5f5';
                    campoUsuario.style.cursor = 'not-allowed';
                    console.log('🔒 Campo Usuario Existente DESHABILITADO');
                }
                
            } else {
                // Deshabilitar y limpiar campos de nuevo usuario
                console.log('🔒 Deshabilitando campos de nuevo usuario...');
                camposNuevoUsuario.forEach(function(fieldId) {
                    var campo = document.getElementById(fieldId);
                    if (campo) {
                        campo.disabled = true;
                        campo.readOnly = true;
                        
                        // Limpiar valor
                        if (fieldId === 'id_is_active') {
                            campo.checked = false;
                        } else {
                            campo.value = '';
                        }
                        
                        // Estilos visuales
                        campo.style.opacity = '0.5';
                        campo.style.backgroundColor = '#f5f5f5';
                        campo.style.cursor = 'not-allowed';
                        
                        console.log('  ✓ Campo deshabilitado:', fieldId);
                    } else {
                        console.warn('  ⚠️ Campo no encontrado:', fieldId);
                    }
                });
                
                // Habilitar campo de usuario existente
                if (campoUsuario) {
                    campoUsuario.disabled = false;
                    campoUsuario.style.opacity = '1';
                    campoUsuario.style.backgroundColor = '';
                    campoUsuario.style.cursor = 'pointer';
                    console.log('✅ Campo Usuario Existente HABILITADO');
                }
            }
        }
        
        // Configurar estado inicial
        console.log('⚙️ Configurando estado inicial...');
        toggleFieldsState();
        
        // Escuchar cambios en el checkbox
        checkboxCrearAuto.addEventListener('change', function() {
            console.log('📝 Checkbox cambiado a:', this.checked);
            toggleFieldsState();
        });
        
        // Prevenir edición de campos deshabilitados (seguridad adicional)
        camposNuevoUsuario.forEach(function(fieldId) {
            var campo = document.getElementById(fieldId);
            if (campo) {
                campo.addEventListener('focus', function() {
                    if (this.disabled || this.readOnly) {
                        this.blur();
                        console.log('⚠️ Intento de editar campo deshabilitado bloqueado:', fieldId);
                    }
                });
                
                // Prevenir teclas
                campo.addEventListener('keydown', function(e) {
                    if (this.disabled || this.readOnly) {
                        e.preventDefault();
                        console.log('⚠️ Tecla bloqueada en campo deshabilitado:', fieldId);
                        return false;
                    }
                });
                
                // Prevenir paste
                campo.addEventListener('paste', function(e) {
                    if (this.disabled || this.readOnly) {
                        e.preventDefault();
                        console.log('⚠️ Paste bloqueado en campo deshabilitado:', fieldId);
                        return false;
                    }
                });
            }
        });
        
        console.log('✅ Script configurado correctamente - Modo habilitar/deshabilitar');
    }
    
})();
