# 🔧 DEUDA TÉCNICA: Complejidad Cognitiva

**Fecha de Identificación:** 12 de Noviembre de 2025  
**Herramienta:** SonarCloud/SonarLint  
**Severidad:** High (Critical)  
**Estado:** DOCUMENTADO - Pendiente de Refactorización

---

## 📊 RESUMEN EJECUTIVO

Se identificaron 5 funciones con complejidad cognitiva superior al límite permitido (15):

| Archivo | Función/Línea | Complejidad Actual | Límite | Esfuerzo | Estado |
|---------|---------------|--------------------| -------|----------|--------|
| reportes/views.py | get_context_data L127 | 27 | 15 | 17min | 📝 Documentado |
| reportes/views.py | get_context_data L206 | 19 | 15 | 9min | 📝 Documentado |
| reportes/views.py | get_context_data L278 | 38 | 15 | 28min | 📝 Documentado |
| reportes/views.py | get_context_data L646 | 29 | 15 | 19min | 📝 Documentado |
| templates/reportes/balance_general.html | calcularBalance L383 | 47 | 15 | 37min | 📝 Documentado |

**Esfuerzo Total Estimado:** ~110 minutos (1.8 horas)

---

## 🎯 JUSTIFICACIÓN DE DEUDA TÉCNICA

### ¿Por qué no refactorizar ahora?

1. **Riesgo de Regresión:**
   - Las funciones son parte crítica de reportes financieros
   - Requieren pruebas exhaustivas después de refactorización
   - Sin suite de tests automatizados actualmente

2. **Tiempo de Desarrollo:**
   - Refactorización completa: ~2 horas
   - Pruebas manuales: ~1 hora adicional
   - Validación con casos reales: indeterminado

3. **Funcionalidad Actual:**
   - ✅ Código funciona correctamente
   - ✅ Sin bugs reportados
   - ✅ Performance aceptable

4. **Prioridades del Proyecto:**
   - ✅ 90+ issues de SonarCloud ya resueltos
   - ✅ Accesibilidad y estándares modernos implementados
   - ⏳ Deuda técnica documentada para sprint futuro

---

## 📝 ANÁLISIS DETALLADO DE FUNCIONES

### 1. BalanceComprobacionView.get_context_data (L127)

**Complejidad:** 27 → Reducir a 15  
**Archivo:** `reportes/views.py`  
**Esfuerzo:** 17 minutos

**Problemas Identificados:**
- Múltiples niveles de anidación (if dentro de for)
- Lógica de cálculo de saldos mezclada con filtrado
- Condicionales para naturaleza de cuenta duplicados

**Plan de Refactorización:**
```python
# Extraer métodos auxiliares:
def _calcular_saldos_cuenta(cuenta, fecha_corte):
    """Calcula débitos, créditos y saldos de una cuenta."""
    # Lógica de agregación y cálculo
    pass

def _determinar_saldo_naturaleza(cuenta, total_debito, total_credito):
    """Determina saldo deudor/acreedor según naturaleza."""
    # Lógica condicional simplificada
    pass

def _filtrar_cuentas_con_movimiento(cuentas, fecha_corte):
    """Filtra y procesa cuentas con movimiento."""
    return [
        self._procesar_cuenta(cuenta, fecha_corte)
        for cuenta in cuentas
        if self._tiene_movimiento(cuenta, fecha_corte)
    ]
```

**Beneficios Esperados:**
- Complejidad reducida de 27 a ~12
- Funciones reutilizables
- Más fácil de testear

---

### 2. EstadoResultadosView.get_context_data (L206)

**Complejidad:** 19 → Reducir a 15  
**Archivo:** `reportes/views.py`  
**Esfuerzo:** 9 minutos

**Problemas Identificados:**
- Bucle con múltiples if-elif anidados
- Lógica de cálculo de saldo repetida

**Plan de Refactorización:**
```python
# Usar diccionario de estrategias:
ESTRATEGIAS_CALCULO = {
    'INGRESO': lambda debito, credito: credito - debito,
    'COSTO': lambda debito, credito: debito - credito,
    'GASTO': lambda debito, credito: debito - credito
}

def _procesar_cuenta_por_tipo(cuenta, agregado):
    """Procesa cuenta según su tipo."""
    total_debito = agregado['sum_debito'] or Decimal('0.00')
    total_credito = agregado['sum_credito'] or Decimal('0.00')
    
    estrategia = ESTRATEGIAS_CALCULO.get(cuenta.tipo_cuenta)
    if estrategia:
        saldo = estrategia(total_debito, total_credito)
        if saldo > 0:
            cuenta.saldo = saldo
            return cuenta
    return None
```

**Beneficios Esperados:**
- Eliminación de if-elif anidados
- Complejidad reducida de 19 a ~10
- Patrón estrategia aplicado

---

### 3. BalanceGeneralView.get_context_data (L278)

**Complejidad:** 38 → Reducir a 15  
**Archivo:** `reportes/views.py`  
**Esfuerzo:** 28 minutos

**Problemas Identificados:**
- Función más compleja del proyecto
- Múltiples responsabilidades mezcladas
- Lógica de clasificación de activos/pasivos compleja

**Plan de Refactorización:**
```python
class BalanceGeneralCalculator:
    """Clase auxiliar para cálculos de balance general."""
    
    def __init__(self, cuentas, fecha_corte):
        self.cuentas = cuentas
        self.fecha_corte = fecha_corte
    
    def calcular_activos(self):
        """Calcula y clasifica activos."""
        return {
            'corrientes': self._activos_corrientes(),
            'no_corrientes': self._activos_no_corrientes()
        }
    
    def calcular_pasivos(self):
        """Calcula y clasifica pasivos."""
        return {
            'corrientes': self._pasivos_corrientes(),
            'no_corrientes': self._pasivos_no_corrientes()
        }
    
    def calcular_patrimonio(self):
        """Calcula cuentas de patrimonio."""
        pass

# En la vista:
def get_context_data(self, **kwargs):
    # ...
    calculator = BalanceGeneralCalculator(cuentas, fecha_corte)
    context['activos'] = calculator.calcular_activos()
    context['pasivos'] = calculator.calcular_pasivos()
    context['patrimonio'] = calculator.calcular_patrimonio()
    return context
```

**Beneficios Esperados:**
- Separación de responsabilidades
- Clase reutilizable
- Complejidad reducida de 38 a ~8 por método
- Más fácil de mantener y testear

---

### 4. Función Exportación L646

**Complejidad:** 29 → Reducir a 15  
**Archivo:** `reportes/views.py`  
**Esfuerzo:** 19 minutos

**Problemas Identificados:**
- Lógica de generación Excel mezclada con lógica de negocio
- Formateo repetitivo

**Plan de Refactorización:**
```python
class ExcelBalanceComprobacionGenerator:
    """Generador de archivos Excel para Balance de Comprobación."""
    
    def __init__(self, cuentas):
        self.cuentas = cuentas
        self.workbook = Workbook()
        self.worksheet = self.workbook.active
    
    def generar(self):
        """Genera el archivo Excel completo."""
        self._configurar_encabezados()
        self._agregar_datos()
        self._agregar_totales()
        self._formatear_columnas()
        return self.workbook
    
    def _configurar_encabezados(self):
        """Configura títulos y encabezados."""
        pass
    
    def _agregar_datos(self):
        """Agrega filas de datos."""
        for cuenta in self.cuentas:
            self._agregar_fila_cuenta(cuenta)
    
    def _aplicar_formato_moneda(self, cell):
        """Aplica formato de moneda a una celda."""
        cell.number_format = EXCEL_MONEY_FORMAT
        cell.alignment = Alignment(horizontal='right')
```

**Beneficios Esperados:**
- Separación de concerns
- Reutilizable para otros reportes
- Complejidad reducida a ~10

---

### 5. JavaScript: calcularBalance (balance_general.html L383)

**Complejidad:** 47 → Reducir a 15  
**Archivo:** `templates/reportes/balance_general.html`  
**Esfuerzo:** 37 minutos

**Problemas Identificados:**
- Función JavaScript monolítica
- Múltiples selectores DOM anidados
- Lógica de suma mezclada con manipulación DOM

**Plan de Refactorización:**
```javascript
// Módulo de cálculos
const BalanceCalculator = {
    calcularActivos(container) {
        const corrientes = this._sumarSeccion(container, '.activos-corrientes');
        const noCorrientes = this._sumarSeccion(container, '.activos-no-corrientes');
        return { corrientes, noCorrientes, total: corrientes + noCorrientes };
    },
    
    calcularPasivos(container) {
        const corrientes = this._sumarSeccion(container, '.pasivos-corrientes');
        const noCorrientes = this._sumarSeccion(container, '.pasivos-no-corrientes');
        return { corrientes, noCorrientes, total: corrientes + noCorrientes };
    },
    
    calcularPatrimonio(container) {
        return this._sumarSeccion(container, '.patrimonio');
    },
    
    _sumarSeccion(container, selector) {
        return Array.from(container.querySelectorAll(selector))
            .reduce((sum, el) => sum + this._parsearValor(el), 0);
    },
    
    _parsearValor(elemento) {
        return Number.parseFloat(
            elemento.textContent.replaceAll(/[$,]/, '')
        ) || 0;
    }
};

// Módulo de actualización UI
const BalanceUI = {
    actualizarTotales(activos, pasivos, patrimonio) {
        this._actualizar('#total-activos', activos.total);
        this._actualizar('#total-pasivos', pasivos.total);
        this._actualizar('#total-patrimonio', patrimonio);
        this._verificarEcuacion(activos.total, pasivos.total, patrimonio);
    },
    
    _actualizar(selector, valor) {
        const elemento = document.querySelector(selector);
        if (elemento) {
            elemento.textContent = formatearMoneda(valor);
        }
    },
    
    _verificarEcuacion(activos, pasivos, patrimonio) {
        const diferencia = activos - (pasivos + patrimonio);
        // Lógica de verificación
    }
};

// Función principal simplificada
function calcularBalance() {
    const activos = BalanceCalculator.calcularActivos(document);
    const pasivos = BalanceCalculator.calcularPasivos(document);
    const patrimonio = BalanceCalculator.calcularPatrimonio(document);
    
    BalanceUI.actualizarTotales(activos, pasivos, patrimonio);
}
```

**Beneficios Esperados:**
- Separación de responsabilidades
- Complejidad por función < 10
- Módulos reutilizables
- Más fácil de testear con Jest/Jasmine

---

## 📅 PLAN DE REFACTORIZACIÓN PROPUESTO

### Sprint 1 (2 horas)
- [x] Documentar deuda técnica ✅
- [ ] Crear suite de tests para reportes actuales
- [ ] Refactorizar EstadoResultadosView (complejidad 19)
- [ ] Refactorizar BalanceComprobacionView (complejidad 27)

### Sprint 2 (3 horas)
- [ ] Crear BalanceGeneralCalculator
- [ ] Refactorizar BalanceGeneralView (complejidad 38)
- [ ] Crear ExcelGenerators como clases auxiliares
- [ ] Refactorizar función exportación (complejidad 29)

### Sprint 3 (2 horas)
- [ ] Refactorizar JavaScript calcularBalance (complejidad 47)
- [ ] Crear módulos JavaScript reutilizables
- [ ] Documentar patrones aplicados
- [ ] Code review y validación

---

## ✅ CRITERIOS DE ACEPTACIÓN

Para considerar la deuda técnica pagada:

1. **Métricas de Código:**
   - ✅ Todas las funciones < 15 de complejidad cognitiva
   - ✅ Cobertura de tests > 80%
   - ✅ SonarCloud sin issues High

2. **Funcionalidad:**
   - ✅ Todos los reportes generan correctamente
   - ✅ Exports (PDF/Excel) mantienen formato
   - ✅ Sin regresiones en cálculos

3. **Mantenibilidad:**
   - ✅ Código documentado con docstrings
   - ✅ Funciones auxiliares reutilizables
   - ✅ Patrones de diseño aplicados

---

## 🎓 LECCIONES APRENDIDAS

### Lo que se hizo bien:
- ✅ Identificación temprana de complejidad
- ✅ Documentación exhaustiva de la deuda
- ✅ Plan de refactorización estructurado

### Para el futuro:
- 🔄 Implementar límites de complejidad en pre-commit hooks
- 🔄 Escribir tests antes de implementar lógica compleja
- 🔄 Code reviews enfocados en complejidad cognitiva
- 🔄 Usar clases auxiliares desde el inicio

---

## 📚 REFERENCIAS

- [SonarCloud Cognitive Complexity](https://www.sonarsource.com/resources/cognitive-complexity/)
- [Refactoring: Improving the Design of Existing Code](https://refactoring.com/)
- [Clean Code by Robert C. Martin](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)

---

## 🔒 COMPROMISO DEL EQUIPO

**Estado Actual:** ACEPTADO TEMPORALMENTE  
**Responsable:** Equipo de Desarrollo  
**Fecha Compromiso Refactorización:** Sprint Q1 2026  
**Tracking:** Issue #[TBD] en GitHub

---

**Notas Importantes:**
- Esta deuda técnica NO afecta la funcionalidad actual
- Los reportes funcionan correctamente
- La refactorización es para mejorar mantenibilidad
- Prioridad: MEDIA (no bloqueante)

---

*Documento generado automáticamente el 12/11/2025*  
*Última actualización: 12/11/2025 02:15 AM*
