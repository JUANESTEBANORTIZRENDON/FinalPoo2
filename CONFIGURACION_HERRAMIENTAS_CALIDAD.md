# Configuración de Herramientas de Calidad de Código
# ====================================================

Este proyecto usa las siguientes herramientas para mantener calidad de código:

- **SonarLint** (enlazado a SonarCloud): Análisis en tiempo real en VS Code
- **Black**: Formateo automático de código Python
- **isort**: Ordenamiento de imports
- **flake8**: Linter de Python (PEP 8)
- **bandit**: Análisis de seguridad
- **pre-commit**: Hooks automáticos antes de commits

## Instalación de Herramientas

### Paso 1: Activar entorno virtual e instalar dependencias

```powershell
# Activar entorno virtual
.\env\Scripts\Activate.ps1

# Instalar todas las dependencias (incluidas las de desarrollo)
pip install -r requirements.txt
```

### Paso 2: Instalar pre-commit hooks

```powershell
# Instalar los hooks de git
pre-commit install

# Probar los hooks manualmente en todos los archivos
pre-commit run --all-files
```

## Uso Diario

### Formatear código automáticamente

```powershell
# Formatear todo el proyecto con Black
black .

# Ordenar imports con isort
isort .

# Ejecutar ambos en archivos modificados
black . && isort .
```

### Verificar calidad del código

```powershell
# Ejecutar flake8 (linter)
flake8 .

# Ejecutar bandit (seguridad)
bandit -r . -c pyproject.toml

# Ejecutar todos los checks de pre-commit
pre-commit run --all-files
```

### Análisis con SonarLint

**En VS Code:**
1. Ctrl+Shift+P → `SonarLint: Analyze this file`
2. Ver problemas en el panel Problems (Ctrl+Shift+M)
3. Corregir antes de hacer commit

## Flujo de Trabajo Recomendado

```
1. Escribir código (con Copilot si quieres)
   ↓
2. SonarLint analiza automáticamente en tiempo real
   ↓
3. Corregir problemas mostrados en Problems panel
   ↓
4. Formatear código: black . && isort .
   ↓
5. git add .
   ↓
6. git commit -m "mensaje"
   ↓
   → Pre-commit hooks se ejecutan automáticamente
   → Si fallan, el commit se cancela
   → Corriges y vuelves a intentar
   ↓
7. git push
   ↓
8. SonarCloud analiza en CI/CD
   ↓
9. Quality Gate aprueba/rechaza
```

## Configuración de VS Code Recomendada

Añade esto a `.vscode/settings.json` (en el workspace):

```json
{
  "editor.formatOnSave": true,
  "python.formatting.provider": "black",
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true
  },
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.pylintEnabled": false
}
```

## Solución de Problemas

### Pre-commit falla en la primera ejecución
```powershell
# Actualizar hooks
pre-commit autoupdate

# Re-ejecutar
pre-commit run --all-files
```

### Black y flake8 entran en conflicto
La configuración en `pyproject.toml` ya está alineada. Si ves conflictos:
- Black tiene prioridad para formateo
- flake8 ignora reglas que entran en conflicto con Black (E203, W503)

### SonarLint no muestra problemas
1. Verifica que esté enlazado a SonarCloud (ver OUTPUT → SonarLint)
2. Ctrl+Shift+P → `SonarLint: Analyze this file`
3. Revisa que el archivo no esté excluido en sonar-project.properties
