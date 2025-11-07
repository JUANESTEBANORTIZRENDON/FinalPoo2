# ⚡ Guía Rápida - Cambio de Contraseña Admin

## 🔐 Contraseña Olvidada - Solución Rápida

### Paso 1: Activar entorno virtual
```bash
.\env\Scripts\Activate.ps1
```

### Paso 2: Ejecutar comando de cambio de contraseña
```bash
python manage.py changepassword admin
```

### Paso 3: Ingresar nueva contraseña
- Ingresa tu nueva contraseña cuando te lo pida
- Confírmala ingresándola de nuevo
- ¡Listo! ✅

---

## 🌐 URLs de Acceso

### Panel de Administración Django
```
URL: http://127.0.0.1:8000/admin/
Usuario: admin
Contraseña: [La que acabas de cambiar]
```

### Panel de Administrador Holding  
```
URL: http://127.0.0.1:8000/empresas/dev-auth/
Contraseña Desarrollador: dev2025secure!
```

---

## 📝 Nueva Contraseña Establecida

**Fecha del cambio:** 06/11/2025

**Usuario:** admin  
**Nueva contraseña:** ✅ Cambiada exitosamente

> ⚠️ **IMPORTANTE:** Guarda tu nueva contraseña en un lugar seguro

---

## 🔄 Si necesitas cambiarla de nuevo

1. Activa el entorno virtual: `.\env\Scripts\Activate.ps1`
2. Ejecuta: `python manage.py changepassword admin`
3. Ingresa la nueva contraseña dos veces

---

## 📚 Documentación Completa

Para más detalles, consulta:
- [Guía Completa de Cambio de Contraseña](./cambio_password_admin.md)
- [Índice de Documentación](./README.md)

---

**Última actualización:** 6 de Noviembre de 2025
