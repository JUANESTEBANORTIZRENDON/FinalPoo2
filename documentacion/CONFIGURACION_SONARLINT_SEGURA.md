# 🔒 Configuración Segura de SonarLint

## ❌ Problema Detectado (secrets:S6702)

SonarLint detectó un **token hardcodeado** en el archivo de configuración de VS Code:
- **Archivo:** `%APPDATA%\Code\User\mcp.json`
- **Línea 19:** `"SONARQUBE_TOKEN": "sqp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"` (ejemplo)
- **Severidad:** 🔴 **CRÍTICO** - Exposición de credenciales

## ✅ Solución Implementada

### 1. Token Movido a Variable de Entorno

El token ha sido removido del archivo `mcp.json` y configurado como variable de entorno del sistema Windows.

**Antes (INSEGURO):**
```json
{
  "env": {
    "SONARQUBE_ORG": "juanestebanortizrendon",
    "SONARQUBE_TOKEN": "sqp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",  // ❌ NUNCA hardcodear
    "SONARQUBE_IDE_PORT": "64120"
  }
}
```

**Después (SEGURO):**
```json
{
  "env": {
    "SONARQUBE_ORG": "juanestebanortizrendon",
    "SONARQUBE_TOKEN": "${env:SONARQUBE_TOKEN}",  ✅
    "SONARQUBE_IDE_PORT": "64120"
  }
}
```

### 2. Configuración de Variable de Entorno

#### Windows (PowerShell)
```powershell
# Configurar variable de entorno de usuario
[Environment]::SetEnvironmentVariable("SONARQUBE_TOKEN", "tu-token-aqui", "User")

# Verificar configuración
$env:SONARQUBE_TOKEN
```

#### Windows (GUI)
1. Presiona `Win + R` → escribe `sysdm.cpl` → Enter
2. Pestaña **"Opciones avanzadas"** → **"Variables de entorno"**
3. En **"Variables de usuario"** → **Nuevo**
4. Nombre: `SONARQUBE_TOKEN`
5. Valor: `tu-token-de-sonarqube`
6. **Reiniciar VS Code** para que tome efecto

### 3. Obtener un Nuevo Token (Recomendado)

Si el token anterior fue expuesto en commits de Git:

1. **Ir a SonarCloud:** https://sonarcloud.io/account/security
2. **Revocar token anterior:** Buscar y eliminar token comprometido
3. **Generar nuevo token:**
   - Nombre: `VS Code - [TU_NOMBRE]`
   - Tipo: `User Token`
   - Alcance: Análisis de código
4. **Copiar token** (solo se muestra una vez)
5. **Configurar nueva variable de entorno:**
   ```powershell
   [Environment]::SetEnvironmentVariable("SONARQUBE_TOKEN", "nuevo-token-aqui", "User")
   ```

## 🔐 Buenas Prácticas de Seguridad

### ✅ DO (Hacer)
- ✅ Usar variables de entorno para tokens
- ✅ Agregar `mcp.json` a `.gitignore` si está en el proyecto
- ✅ Rotar tokens periódicamente (cada 3-6 meses)
- ✅ Usar tokens con permisos mínimos necesarios
- ✅ Documentar configuración sin exponer valores

### ❌ DON'T (No hacer)
- ❌ Hardcodear tokens en archivos de configuración
- ❌ Commitear tokens en Git
- ❌ Compartir tokens en screenshots o documentación
- ❌ Usar el mismo token para múltiples propósitos
- ❌ Dejar tokens con permisos excesivos

## 📋 Verificación de Configuración

### Verificar que la variable de entorno está configurada:
```powershell
# PowerShell
$env:SONARQUBE_TOKEN
# Debería mostrar tu token (no lo compartas)

# Verificar que mcp.json usa la variable
Get-Content "$env:APPDATA\Code\User\mcp.json" | Select-String "SONARQUBE_TOKEN"
# Debería mostrar: "SONARQUBE_TOKEN": "${env:SONARQUBE_TOKEN}"
```

### Verificar que SonarLint funciona:
1. Reiniciar VS Code completamente
2. Abrir un archivo Python del proyecto
3. SonarLint debería analizar sin errores de autenticación
4. Verificar panel "PROBLEMS" → pestañas "SONARQUBE"

## 🚨 Si el Token fue Expuesto en Git

### 1. Revocar inmediatamente en SonarCloud
- URL: https://sonarcloud.io/account/security

### 2. Generar nuevo token

### 3. Limpiar historial de Git (opcional, para casos críticos)
```bash
# ⚠️ CUIDADO: Reescribe historial de Git
git filter-branch --tree-filter 'find . -name "mcp.json" -exec sed -i "s/sqp_[a-zA-Z0-9]\{40\}/TOKEN_REMOVED/g" {} \;' HEAD
```

## 🔗 Referencias

- [SonarCloud Security Best Practices](https://docs.sonarcloud.io/advanced-setup/security/)
- [SonarLint Connected Mode](https://docs.sonarsource.com/sonarlint/vs-code/team-features/connected-mode/)
- [Git Secrets Management](https://git-scm.com/book/en/v2/Git-Tools-Credential-Storage)

---

**Fecha de corrección:** 2025-11-10  
**Commit relacionado:** 6083150 (correcciones Pylance)  
**Issue SonarCloud:** secrets:S6702  
**Severidad:** 🔴 Blocker  
**Estado:** ✅ Resuelto
