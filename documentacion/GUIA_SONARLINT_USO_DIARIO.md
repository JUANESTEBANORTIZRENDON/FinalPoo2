# GUÍA RÁPIDA: Uso Diario de SonarLint en VS Code

## 🚦 Verificar Estado de SonarLint

### 1. Mirar la Barra de Estado (abajo en VS Code)
Deberías ver un ícono de SonarLint (🔵 o ⚪):
- 🔵 **Azul/Verde**: Conectado y funcionando
- 🔴 **Rojo**: Desconectado o con problemas
- ⚪ **Gris**: Inactivo

### 2. Abrir Panel de Problemas
**Atajo**: `Ctrl + Shift + M` (Windows/Linux) o `Cmd + Shift + M` (Mac)

En el panel verás:
- ❌ **Errores** (bugs críticos)
- ⚠️ **Warnings** (code smells, sugerencias)
- ℹ️ **Info** (mejoras menores)

### 3. Ver Detalles de un Issue
1. Haz clic en cualquier línea subrayada con ondas (~~~)
2. Aparecerá un tooltip con:
   - **Descripción del problema**
   - **Por qué es importante**
   - **Cómo solucionarlo**
   - **Link a documentación**

## 📝 Workflow Recomendado

### Mientras Escribes Código:
```
1. Escribes función → SonarLint analiza automáticamente
2. Aparece subrayado rojo/amarillo → Lees el mensaje
3. Decides: ¿Lo arreglo ahora o después?
4. Click derecho → "Quick Fix" (si hay solución automática)
```

### Antes de Hacer Commit:
```
1. Abre Panel de Problemas (Ctrl+Shift+M)
2. Filtra por "SonarLint"
3. Revisa issues críticos (❌)
4. Arregla o justifica (comentario # nosonar)
5. Verifica que no hay issues bloqueantes
6. Haz commit
```

## 🎯 Comandos Útiles de SonarLint

### En Command Palette (Ctrl+Shift+P):
- `SonarLint: Analyze all open files` - Analiza todos los archivos abiertos
- `SonarLint: Show SonarLint Output` - Muestra log de análisis
- `SonarLint: Update all project bindings` - Sincroniza reglas con servidor
- `SonarLint: Clear SonarLint issues` - Limpia issues antiguos

## 🔍 Interpretar Issues de SonarLint

### Severidad (de más grave a menos):
1. **BLOCKER** 🔴 - Bug crítico, bloquea deployment
2. **CRITICAL** 🟠 - Vulnerabilidad de seguridad o bug grave
3. **MAJOR** 🟡 - Code smell importante
4. **MINOR** 🟢 - Mejora menor
5. **INFO** 🔵 - Sugerencia opcional

### Tipos de Issues:
- **BUG**: Error lógico que causa comportamiento incorrecto
- **VULNERABILITY**: Agujero de seguridad
- **CODE_SMELL**: Código funcional pero mal diseñado
- **SECURITY_HOTSPOT**: Código sensible que requiere revisión manual

## 💡 Ejemplo Práctico

```python
# ❌ SonarLint detectará: "Cognitive Complexity of 25 exceeds limit of 15"
def procesar_pedido(pedido):
    if pedido.valido:
        if pedido.tipo == 'urgente':
            if pedido.pago == 'tarjeta':
                if pedido.monto > 1000:
                    # ... 20 líneas más de ifs anidados
                    pass

# ✅ Solución: Extraer funciones (como hicimos en views_admin.py)
def procesar_pedido(pedido):
    if not pedido.valido:
        return None
    return _procesar_por_tipo(pedido)

def _procesar_por_tipo(pedido):
    if pedido.tipo == 'urgente':
        return _procesar_urgente(pedido)
    # ...
```

## 🚫 Suprimir Issues (Úsalo con Cuidado)

### Opción 1: Comentario inline
```python
def mi_funcion():  # nosonar
    # SonarLint ignorará esta línea
    pass
```

### Opción 2: Marcar como "Won't Fix" en SonarCloud
- Solo para issues que revisaste y decidiste no arreglar
- Requiere justificación escrita

## 🔗 Sincronización con SonarCloud

### Cómo funciona:
1. SonarLint lee reglas de SonarCloud cada X horas
2. Si cambias configuración en SonarCloud, ejecuta:
   ```
   Ctrl+Shift+P → "SonarLint: Update all project bindings"
   ```
3. Issues resueltos en SonarCloud desaparecen de VS Code

### Beneficios del Modo Conectado:
- ✅ Mismo conjunto de reglas que tu equipo
- ✅ Issues consistentes entre local y CI/CD
- ✅ Quality Gates visibles antes de commit
- ✅ Sincroniza suppressions (# nosonar)

---

**💡 TIP PRO**: Configura auto-save en VS Code para que SonarLint analice mientras escribes:
```json
// .vscode/settings.json
{
    "files.autoSave": "afterDelay",
    "files.autoSaveDelay": 1000
}
```
