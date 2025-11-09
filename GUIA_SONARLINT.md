# Guía Rápida: SonarLint Conectado a SonarCloud

## ✅ Configuración Actual

**SonarLint** está conectado a tu proyecto en **SonarCloud**:
- Organización: `juanestebanortizrendon`
- Proyecto: `JUANESTEBANORTIZRENDON_FinalPoo2`

## 📍 Cómo Ver los Problemas que Marca SonarLint

### **Opción 1: Panel de Problemas (Problems)**

El lugar principal para ver todos los issues:

1. **Abrir el panel**:
   - Atajo: `Ctrl + Shift + M`
   - O menú: `View → Problems`

2. **Qué verás**:
   - Lista de todos los problemas detectados
   - Archivo y línea donde está el problema
   - Descripción del issue
   - Severidad (🔴 Error, 🟡 Warning, ℹ️ Info)

3. **Navegar**:
   - Click en cualquier problema → te lleva directamente a la línea de código
   - Doble click → abre el archivo y posiciona el cursor

### **Opción 2: En el Editor (Líneas Subrayadas)**

Mientras escribes código:

1. **Líneas rojas/amarillas**: SonarLint marca problemas con subrayado
   - 🔴 Rojo ondulado = Bug o vulnerabilidad
   - 🟡 Amarillo ondulado = Code smell o mejora sugerida

2. **Ver detalles**:
   - Pasa el mouse sobre la línea marcada
   - Aparece un tooltip con:
     - Nombre de la regla (ej: `python:S1234`)
     - Explicación del problema
     - Cómo corregirlo

3. **Quick Fix**:
   - Posiciona el cursor en la línea marcada
   - Presiona `Ctrl + .` (punto)
   - Si hay solución automática, aparece "Quick Fix"

### **Opción 3: Output de SonarLint**

Para ver el log detallado de análisis:

1. **Abrir Output**:
   - Menú: `View → Output`
   - O atajo: `Ctrl + Shift + U`

2. **Seleccionar canal SonarLint**:
   - En el dropdown de arriba a la derecha del panel
   - Selecciona: **"SonarLint"**

3. **Qué verás**:
   - Log de conexión a SonarCloud
   - Archivos analizados
   - Tiempo de análisis
   - Errores de conexión (si los hay)

### **Opción 4: Análisis Manual**

Forzar análisis de un archivo:

1. **Abre el archivo** que quieres analizar

2. **Comando Palette**:
   - `Ctrl + Shift + P`

3. **Ejecuta**:
   - Escribe: `SonarLint: Analyze this file`
   - O: `SonarLint: Analyze all open files`

4. **Resultados**:
   - Aparecen en el Panel de Problemas (Ctrl+Shift+M)

## 🔍 Filtrar Problemas

En el Panel de Problemas (Ctrl+Shift+M):

1. **Por tipo**:
   - Click en los iconos de filtro arriba
   - Puedes mostrar/ocultar Errors, Warnings, Info

2. **Por archivo**:
   - Los problemas están agrupados por archivo
   - Expande/colapsa con las flechitas

3. **Buscar texto**:
   - Usa el campo de búsqueda en el panel
   - Filtra por nombre de archivo o texto del problema

## 🎯 Flujo de Trabajo Recomendado

```
1. Escribes código (con Copilot si quieres)
   ↓
2. SonarLint analiza automáticamente (1-2 segundos)
   ↓
3. Ves problemas en el editor (líneas subrayadas)
   ↓
4. Abres Panel de Problemas (Ctrl+Shift+M) para ver todo
   ↓
5. Corriges problemas uno por uno
   - Click en problema → te lleva al código
   - Pasas mouse sobre línea → ves explicación
   - Ctrl+. → intentas Quick Fix si está disponible
   ↓
6. Guardas archivo (Ctrl+S)
   ↓
7. SonarLint re-analiza y verifica corrección
   ↓
8. Commit cuando no hay problemas críticos
```

## ⚙️ Comandos Útiles de SonarLint

Todos desde Command Palette (`Ctrl+Shift+P`):

- `SonarLint: Analyze this file` - Analizar archivo actual
- `SonarLint: Analyze all open files` - Analizar todos los abiertos
- `SonarLint: Show all locations for rule` - Ver todas las violaciones de una regla
- `SonarLint: Update all project bindings to SonarQube/SonarCloud` - Sincronizar reglas

## 🔗 Conexión a SonarCloud

**Estado actual**: ✅ Conectado

**Verificar conexión**:
1. Output → SonarLint
2. Busca línea: `Connected to SonarQube/SonarCloud server 'juanestebanortizrendon'`

**Si hay problemas de conexión**:
1. Ctrl+Shift+P → `SonarLint: Edit SonarQube/SonarCloud Connection`
2. Selecciona tu conexión
3. Verifica token y proyecto

## 📊 Tipos de Issues

SonarLint detecta:

- 🔴 **Bugs**: Errores que causan comportamiento incorrecto
- 🛡️ **Vulnerabilities**: Problemas de seguridad
- 🟡 **Code Smells**: Código difícil de mantener
- 🔒 **Security Hotspots**: Áreas sensibles que revisar

## ⚡ Atajos de Teclado

- `Ctrl+Shift+M` - Abrir/cerrar Panel de Problemas
- `F8` - Ir al siguiente problema
- `Shift+F8` - Ir al problema anterior
- `Ctrl+.` - Quick Fix en línea actual
- `Ctrl+Shift+P` → `SonarLint:...` - Comandos de SonarLint

## 💡 Consejos

1. **No ignores warnings**: Los code smells acumulados dificultan mantenimiento
2. **Lee las explicaciones**: SonarLint explica por qué algo es problema
3. **Aprende de los issues**: Con el tiempo memorizas las reglas
4. **Analiza antes de commit**: Ctrl+Shift+M antes de hacer commit
5. **Sincroniza con SonarCloud**: Las reglas se actualizan del servidor

## 🚫 Lo que SonarLint NO hace

- ❌ No bloquea commits (no hay pre-commit hooks)
- ❌ No formatea código automáticamente
- ❌ No cambia tu código sin tu permiso
- ❌ No hace que Copilot respete reglas

**Solo MUESTRA problemas. TÚ decides qué corregir y cuándo.**

## 🎯 Objetivo

Con SonarLint conectado a SonarCloud:
- Ves problemas mientras desarrollas (local)
- GitHub Actions + SonarCloud validan en CI/CD (remoto)
- Ambos usan las MISMAS reglas (sincronizadas)
- Detectas y corriges problemas antes de push

---

**¿Problemas? Revisa el Output de SonarLint (Ctrl+Shift+U → SonarLint)**
