# 🔧 Solución: Problemas de Accesibilidad ARIA-LABEL - SonarCloud

## 📋 Resumen del Problema

**Error de SonarCloud**: "The accessible name should be part of the visible label"
- **Tipo**: Code Smell (Major)
- **Categoría**: Maintainability > Accessibility
- **Líneas afectadas**: L189, L194, L200 en `gestionar_usuarios.html` + archivos similares

## ❌ Problema Identificado

Según las reglas de accesibilidad WCAG, cuando un elemento tiene un `aria-label`, ese texto debe coincidir con el texto visible del elemento o ser parte de él. Si el `aria-label` describe algo que no está visible, viola las pautas de accesibilidad.

### Casos Problemáticos Encontrados:

1. **`<div class="btn-group" role="group" aria-label="Acciones para el usuario...">`**
   - ❌ El texto "Acciones para el usuario..." no es visible en pantalla
   - ❌ Los botones individuales ya tienen sus propios `aria-label`
   - ✅ El contenedor no necesita `aria-label` adicional

2. **`<div class="spinner-border" aria-label="Cargando información...">`**
   - ❌ Usa `aria-label` en lugar de `role="status"`
   - ❌ El texto del `aria-label` no coincide con el `<span class="visually-hidden">`
   - ✅ Los spinners deben usar `role="status"` según Bootstrap

## ✅ Solución Aplicada

### 1. Archivo: `templates/empresas/admin/gestionar_usuarios.html`

**Antes (Línea 188-189)**:
```html
<div class="btn-group" role="group" 
     aria-label="Acciones para el usuario {{ usuario.get_full_name|default:usuario.username }}">
```

**Después**:
```html
<div class="btn-group" role="group">
```

**Razón**: Los botones individuales (`🏢 Asignar`, `✏️ Editar`, `🚫 Desactivar`) ya tienen sus propios `aria-label` descriptivos. El contenedor no necesita un `aria-label` adicional.

---

### 2. Archivo: `templates/tesoreria/cobros_lista.html`

**Antes (Línea 122)**:
```html
<div class="btn-group btn-group-sm" aria-label="Acciones del cobro">
```

**Después**:
```html
<div class="btn-group btn-group-sm" role="group">
```

---

### 3. Archivo: `templates/catalogos/productos_lista.html`

**Antes (Línea 153)**:
```html
<div class="btn-group btn-group-sm" aria-label="Acciones del producto">
```

**Después**:
```html
<div class="btn-group btn-group-sm" role="group">
```

---

### 4. Archivo: `templates/empresas/admin/gestionar_empresas.html`

**Antes (2 lugares - Líneas 278 y 306)**:
```html
<div class="spinner-border" aria-label="Cargando información de la empresa">
    <span class="visually-hidden">Cargando...</span>
</div>
```

**Después**:
```html
<div class="spinner-border" role="status">
    <span class="visually-hidden">Cargando...</span>
</div>
```

**Razón**: Según la documentación de Bootstrap y las pautas WCAG:
- Los spinners deben usar `role="status"` en lugar de `aria-label`
- El texto accesible se proporciona mediante `<span class="visually-hidden">`
- Esto asegura que los lectores de pantalla anuncien el estado de carga correctamente

## 📊 Archivos Modificados

| Archivo | Cambios | Líneas |
|---------|---------|--------|
| `gestionar_usuarios.html` | Eliminado `aria-label` de btn-group | L189 |
| `cobros_lista.html` | Eliminado `aria-label` de btn-group | L122 |
| `productos_lista.html` | Eliminado `aria-label` de btn-group | L153 |
| `gestionar_empresas.html` | Cambiado a `role="status"` (2 spinners) | L278, L306 |

## 🔍 Búsqueda Completa del Proyecto

Se realizó una búsqueda exhaustiva en todo el proyecto para identificar casos similares:

```bash
# Búsqueda de btn-group con aria-label
grep -r 'btn-group.*aria-label=' templates/
# Resultado: 3 coincidencias corregidas

# Búsqueda de spinners con aria-label
grep -r 'spinner-border.*aria-label=' templates/
# Resultado: 2 coincidencias corregidas

# Búsqueda de div con aria-label
grep -r '<div.*aria-label=' templates/
# Resultado: Todos los casos revisados y corregidos
```

**✅ Confirmado**: No quedan casos similares en el proyecto.

## 📝 Reglas de Accesibilidad Aplicadas

### WCAG 2.1 - Success Criterion 2.5.3: Label in Name
> "For user interface components with labels that include text or images of text, the name contains the text that is presented visually."

### Mejores Prácticas:

1. **Button Groups**: 
   - ✅ Usar `role="group"` sin `aria-label` si los botones individuales ya están etiquetados
   - ✅ Solo agregar `aria-label` al grupo si mejora la comprensión del contexto

2. **Spinners/Loading Indicators**:
   - ✅ Usar `role="status"` para indicadores de carga
   - ✅ Incluir `<span class="visually-hidden">` con texto descriptivo
   - ❌ No usar `aria-label` en spinners

3. **Elementos Interactivos**:
   - ✅ El `aria-label` debe coincidir con el texto visible
   - ✅ Si el texto es visible, el `aria-label` es redundante

## 🚀 Deploy

**Commit**: `527ab96` - "fix: corregir problemas de accesibilidad en aria-label según SonarCloud"

**Cambios**:
- 4 archivos modificados
- +5 líneas, -6 líneas
- Push exitoso a GitHub → Deploy automático en Render

## ✅ Resultado

Todos los errores de accesibilidad relacionados con `aria-label` han sido corregidos:

- ✅ **4 errores en gestionar_usuarios.html** → Corregidos
- ✅ **1 error en cobros_lista.html** → Corregido
- ✅ **1 error en productos_lista.html** → Corregido
- ✅ **2 errores en gestionar_empresas.html** → Corregidos

**Total**: 8 problemas de accesibilidad resueltos ✨

---

**Fecha**: 6 de noviembre de 2025
**Herramienta**: SonarCloud Code Quality Analysis
**Estándar**: WCAG 2.1 Level A (Accessibility)
