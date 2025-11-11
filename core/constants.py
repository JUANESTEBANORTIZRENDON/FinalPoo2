"""
Constantes comunes para mensajes y validaciones
Reduce duplicación de literales en todo el proyecto
"""

# === MENSAJES DE ERROR ===
MSG_NO_PERMISOS = 'No tienes permisos para acceder a esta sección.'
MSG_SELECCIONAR_EMPRESA = 'Debes seleccionar una empresa.'
MSG_ERROR_GENERICO = 'Ha ocurrido un error. Por favor, intenta nuevamente.'
MSG_CAMPOS_REQUERIDOS = 'Por favor, completa todos los campos requeridos.'
MSG_USUARIO_NO_ENCONTRADO = 'Usuario no encontrado.'
MSG_EMPRESA_NO_ENCONTRADA = 'Empresa no encontrada.'

# === MENSAJES DE ÉXITO ===
MSG_CREADO_EXITOSAMENTE = '{} creado exitosamente.'
MSG_ACTUALIZADO_EXITOSAMENTE = '{} actualizado exitosamente.'
MSG_ELIMINADO_EXITOSAMENTE = '{} eliminado exitosamente.'
MSG_GUARDADO_EXITOSAMENTE = 'Los cambios se guardaron exitosamente.'

# === MENSAJES DE ADVERTENCIA ===
MSG_CAMBIOS_NO_GUARDADOS = 'Tienes cambios sin guardar. ¿Deseas continuar?'
MSG_ACCION_IRREVERSIBLE = 'Esta acción es irreversible. ¿Deseas continuar?'

# === URLS COMUNES ===
URL_LOGIN = 'accounts:login'
URL_DASHBOARD = 'accounts:dashboard'
URL_ADMIN_DASHBOARD = 'empresas:admin_dashboard'
URL_CAMBIAR_EMPRESA = 'empresas:cambiar_empresa'

# === ESTILOS CSS REUTILIZABLES ===
STYLE_MUTED_TEXT = "color: #999;"
STYLE_MUTED_SMALL_TEXT = "color: #999; font-size: 0.8em;"
STYLE_SUCCESS_TEXT = "color: #28a745;"
STYLE_ERROR_TEXT = "color: #dc3545;"
STYLE_WARNING_TEXT = "color: #ffc107;"

# === ESTADOS COMUNES ===
ESTADO_ACTIVO = 'activo'
ESTADO_INACTIVO = 'inactivo'
ESTADO_PENDIENTE = 'pendiente'
ESTADO_CONFIRMADO = 'confirmado'
ESTADO_ANULADO = 'anulado'

# === AYUDA PARA FORMULARIOS ===
HELP_TEXT_IS_ACTIVE = "Determina si el usuario puede iniciar sesión"
HELP_TEXT_REQUIRED = "Este campo es obligatorio"
HELP_TEXT_OPTIONAL = "Este campo es opcional"

# === PAGINACIÓN ===
DEFAULT_PAGINATE_BY = 50
MAX_PAGINATE_BY = 100

# === FORMATOS DE FECHA ===
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DISPLAY_DATE_FORMAT = '%d/%m/%Y'
DISPLAY_DATETIME_FORMAT = '%d/%m/%Y %H:%M'
