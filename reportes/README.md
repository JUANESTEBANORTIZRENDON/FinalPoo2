# 📊 Módulo de Reportes Contables – Explicación General

Este módulo se encarga de generar los **reportes financieros y contables** que toda empresa necesita para conocer su situación económica, cumplir con obligaciones legales y tomar decisiones estratégicas.

---

## 📚 Reportes Contables Disponibles

1. 📖 **Libro Diario**
2. 📗 **Libro Mayor**
3. ⚖️ **Balance de Comprobación**
4. 💰 **Estado de Resultados**
5. 📊 **Balance General**

---

## 📖 1. Libro Diario

### ¿Qué es?
El **Libro Diario** es el registro **cronológico** (ordenado por fecha) de **TODOS** los asientos contables que se han hecho en la empresa.

### ¿Para qué sirve?
- Ver el historial completo de operaciones día a día
- Auditoría y control de todas las transacciones
- Obligatorio por ley para efectos fiscales

### 🔹 Ejemplo:

```
LIBRO DIARIO - Noviembre 2025
════════════════════════════════════════════════════════════

Fecha: 01/11/2025 | Asiento #001
Concepto: Venta de mercancía de contado
┌──────────────────────────┬──────────┬──────────┐
│ Cuenta                   │ Débito   │ Crédito  │
├──────────────────────────┼──────────┼──────────┤
│ 1105 - Caja              │ 500.000  │    —     │
│ 4105 - Ingresos ventas   │    —     │ 500.000  │
└──────────────────────────┴──────────┴──────────┘

Fecha: 05/11/2025 | Asiento #002
Concepto: Pago arriendo oficina
┌──────────────────────────┬──────────┬──────────┐
│ Cuenta                   │ Débito   │ Crédito  │
├──────────────────────────┼──────────┼──────────┤
│ 5105 - Gasto arriendo    │ 800.000  │    —     │
│ 1110 - Banco             │    —     │ 800.000  │
└──────────────────────────┴──────────┴──────────┘

... y así sucesivamente con TODOS los asientos del período
```

### 📘 En palabras simples:
Es como un **diario personal** donde escribes TODO lo que pasa contablemente, en el orden en que sucede.

---

## 📗 2. Libro Mayor

### ¿Qué es?
El **Libro Mayor** agrupa todos los movimientos por **cada cuenta contable**. Mientras el Libro Diario muestra asientos completos, el Libro Mayor muestra el detalle de UNA cuenta específica.

### ¿Para qué sirve?
- Ver el historial de movimientos de una cuenta específica
- Conocer el saldo actual de cualquier cuenta
- Analizar el comportamiento de gastos, ingresos, activos, etc.

### 🔹 Ejemplo - Cuenta "Banco":

```
LIBRO MAYOR - Cuenta: 1110 BANCO
════════════════════════════════════════════════════════════

Fecha      | Concepto              | Débito    | Crédito   | Saldo
───────────┼──────────────────────┼──────────┼──────────┼──────────
01/11/2025 | Saldo inicial         |    —      |    —      | 5.000.000
03/11/2025 | Cobro factura #001    | 1.200.000 |    —      | 6.200.000
05/11/2025 | Pago arriendo         |    —      |  800.000  | 5.400.000
08/11/2025 | Pago proveedor        |    —      |  300.000  | 5.100.000
10/11/2025 | Cobro factura #002    |  500.000  |    —      | 5.600.000
───────────┴──────────────────────┴──────────┴──────────┴──────────
                      SALDO FINAL:                         5.600.000
```

### 🔹 Ejemplo - Cuenta "Gastos de Servicios":

```
LIBRO MAYOR - Cuenta: 5120 GASTOS DE SERVICIOS PÚBLICOS
════════════════════════════════════════════════════════════

Fecha      | Concepto              | Débito    | Crédito   | Saldo
───────────┼──────────────────────┼──────────┼──────────┼──────────
01/11/2025 | Saldo inicial         |    —      |    —      |      0
02/11/2025 | Pago luz              |  150.000  |    —      |  150.000
15/11/2025 | Pago agua             |   80.000  |    —      |  230.000
20/11/2025 | Pago internet         |  120.000  |    —      |  350.000
───────────┴──────────────────────┴──────────┴──────────┴──────────
                      SALDO FINAL:                          350.000
```

### 📘 En palabras simples:
Es como tener un **extracto bancario** pero para CADA cuenta contable. Te dice cuánto entra, cuánto sale y cuánto queda en cada cuenta.

---

## ⚖️ 3. Balance de Comprobación

### ¿Qué es?
El **Balance de Comprobación** (o Balance de Prueba) es un resumen que muestra el **saldo de TODAS las cuentas** en un momento determinado. Es como tomar una "foto" de la contabilidad completa.

### ¿Para qué sirve?
- Verificar que la contabilidad esté cuadrada (débitos = créditos)
- Detectar errores antes de hacer estados financieros
- Base para preparar el Estado de Resultados y Balance General

### 🔹 Ejemplo:

```
BALANCE DE COMPROBACIÓN - Al 30/11/2025
════════════════════════════════════════════════════════════════════

Código | Cuenta                    | Débitos    | Créditos   | Saldo Deudor | Saldo Acreedor
───────┼──────────────────────────┼───────────┼───────────┼──────────────┼────────────────
1105   | Caja                      | 2.500.000  |  500.000   |  2.000.000   |      —
1110   | Banco                     | 8.000.000  | 2.400.000  |  5.600.000   |      —
1305   | Clientes                  | 3.000.000  | 1.000.000  |  2.000.000   |      —
1435   | Inventarios               | 5.000.000  | 2.000.000  |  3.000.000   |      —
2105   | Proveedores               |  800.000   | 1.500.000  |      —       |   700.000
2365   | Impuestos por pagar       |    —       |  300.000   |      —       |   300.000
3105   | Capital                   |    —       | 10.000.000 |      —       | 10.000.000
4105   | Ingresos por ventas       |    —       | 8.000.000  |      —       |  8.000.000
5105   | Gastos de arriendo        | 1.600.000  |    —       |  1.600.000   |      —
5120   | Gastos de servicios       |  400.000   |    —       |    400.000   |      —
───────┴──────────────────────────┴───────────┴───────────┴──────────────┴────────────────
TOTALES:                           21.300.000   21.300.000   14.600.000     14.600.000 ✅
```

### 📘 En palabras simples:
Es una **hoja de resumen** donde ves todas tus cuentas con sus saldos. Si todo está bien, los débitos totales deben ser iguales a los créditos totales.

---

## 💰 4. Estado de Resultados

### ¿Qué es?
El **Estado de Resultados** (o Estado de Pérdidas y Ganancias - P&G) muestra si la empresa **ganó o perdió dinero** en un período determinado.

### ¿Para qué sirve?
- Saber si el negocio es rentable
- Tomar decisiones sobre costos y precios
- Presentar a socios, inversionistas o bancos
- Declaración de impuestos (base gravable)

### 🔹 Estructura:

```
ESTADO DE RESULTADOS
Período: Enero 01 - Noviembre 30, 2025
════════════════════════════════════════════════════════════

📈 INGRESOS
   Ingresos por ventas                          12.000.000
   Otros ingresos                                  500.000
   ─────────────────────────────────────────────────────────
   TOTAL INGRESOS                               12.500.000

📉 COSTOS Y GASTOS
   Costo de mercancía vendida                   -5.000.000
   ─────────────────────────────────────────────────────────
   UTILIDAD BRUTA                                7.500.000

   Gastos de administración:
      ├─ Sueldos                                -2.000.000
      ├─ Arriendo                               -1.600.000
      ├─ Servicios públicos                       -400.000
      └─ Papelería                                -100.000
   
   Gastos de ventas:
      ├─ Publicidad                               -300.000
      └─ Comisiones                               -200.000
   ─────────────────────────────────────────────────────────
   TOTAL GASTOS OPERACIONALES                   -4.600.000

   UTILIDAD OPERACIONAL                          2.900.000

   Gastos financieros (intereses)                 -150.000
   ─────────────────────────────────────────────────────────
   UTILIDAD ANTES DE IMPUESTOS                   2.750.000

   Impuesto de renta (35%)                        -962.500
   ─────────────────────────────────────────────────────────
   
✅ UTILIDAD NETA                                 1.787.500
```

### 📘 En palabras simples:
Es como una **calculadora de ganancias**:
```
Ingresos - Costos - Gastos = ¿Ganancia o Pérdida?
```

Si el resultado es **positivo** → Ganaste dinero 💰  
Si el resultado es **negativo** → Perdiste dinero 📉

---

## 📊 5. Balance General

### ¿Qué es?
El **Balance General** (o Estado de Situación Financiera) muestra **qué tiene la empresa** (Activos), **qué debe** (Pasivos) y **cuánto vale realmente** (Patrimonio) en un momento específico.

### ¿Para qué sirve?
- Conocer la situación financiera real del negocio
- Evaluar solvencia y capacidad de pago
- Solicitar créditos o inversiones
- Cumplir obligaciones legales y fiscales

### 🔹 Ecuación Fundamental:

```
ACTIVOS = PASIVOS + PATRIMONIO
(Lo que tengo) = (Lo que debo) + (Lo que es mío)
```

### 🔹 Estructura:

```
BALANCE GENERAL
Al 30 de Noviembre de 2025
════════════════════════════════════════════════════════════

🔷 ACTIVOS (Lo que tenemos)

   ACTIVOS CORRIENTES (corto plazo):
      ├─ Caja                                     2.000.000
      ├─ Bancos                                   5.600.000
      ├─ Clientes (cuentas por cobrar)            2.000.000
      └─ Inventarios                              3.000.000
      ─────────────────────────────────────────────────────
      TOTAL ACTIVOS CORRIENTES                   12.600.000

   ACTIVOS NO CORRIENTES (largo plazo):
      ├─ Muebles y enseres                        1.500.000
      ├─ Equipos de cómputo                       2.000.000
      └─ Vehículos                                8.000.000
      ─────────────────────────────────────────────────────
      TOTAL ACTIVOS NO CORRIENTES                11.500.000

   TOTAL ACTIVOS                                 24.100.000
   ═════════════════════════════════════════════════════════

🔶 PASIVOS (Lo que debemos)

   PASIVOS CORRIENTES (corto plazo):
      ├─ Proveedores (cuentas por pagar)            700.000
      ├─ Impuestos por pagar                        300.000
      └─ Obligaciones laborales                     200.000
      ─────────────────────────────────────────────────────
      TOTAL PASIVOS CORRIENTES                    1.200.000

   PASIVOS NO CORRIENTES (largo plazo):
      └─ Préstamos bancarios                      2.900.000
      ─────────────────────────────────────────────────────
      TOTAL PASIVOS NO CORRIENTES                 2.900.000

   TOTAL PASIVOS                                  4.100.000
   ═════════════════════════════════════════════════════════

🔷 PATRIMONIO (Lo que realmente es nuestro)

      ├─ Capital inicial                         10.000.000
      ├─ Reservas                                 2.000.000
      ├─ Utilidades acumuladas                    6.212.500
      └─ Utilidad del ejercicio                   1.787.500
      ─────────────────────────────────────────────────────
      TOTAL PATRIMONIO                           20.000.000

   ═════════════════════════════════════════════════════════
   TOTAL PASIVO + PATRIMONIO                     24.100.000 ✅
```

### 📘 En palabras simples:
Es como una **radiografía financiera** de tu empresa en un día específico:

- **ACTIVOS**: Todo lo que tienes (dinero, productos, equipos, edificios)
- **PASIVOS**: Todo lo que debes (proveedores, préstamos, impuestos)
- **PATRIMONIO**: Lo que realmente es tuyo después de pagar todas las deudas

**Ejemplo analógico:**
```
Imagina que tu empresa es como una casa:

Activos = La casa vale $100 millones
Pasivos = Debes al banco $40 millones (hipoteca)
Patrimonio = Lo que realmente es tuyo = $60 millones
```

---

## 🔄 Relación entre los Reportes

```
┌────────────────┐
│  LIBRO DIARIO  │ ──┐
└────────────────┘   │
                     ├──> Alimentan los datos
┌────────────────┐   │
│  LIBRO MAYOR   │ ──┘
└────────────────┘
         │
         │ Resumen
         ↓
┌────────────────────────┐
│ BALANCE DE COMPROBACIÓN│
└────────────────────────┘
         │
         │ Se divide en
         ├──────────────┬─────────────┐
         ↓              ↓             ↓
┌─────────────────┐  ┌──────────────────┐
│ ESTADO DE       │  │ BALANCE GENERAL  │
│ RESULTADOS      │  │                  │
│                 │  │ ├─ Activos       │
│ Ingresos        │  │ ├─ Pasivos       │
│ - Gastos        │  │ └─ Patrimonio    │
│ = Utilidad ─────┼──┘                  │
└─────────────────┘  └──────────────────┘
```

---

## 📅 Periodicidad de los Reportes

| Reporte | Frecuencia Típica |
|---------|-------------------|
| **Libro Diario** | Diario / Mensual (para consulta) |
| **Libro Mayor** | Mensual / Cuando se necesite |
| **Balance de Comprobación** | Mensual (antes de cierre) |
| **Estado de Resultados** | Mensual / Trimestral / Anual |
| **Balance General** | Trimestral / Anual (obligatorio) |

---

## 🎯 ¿Cuándo usar cada reporte?

### Usa el **Libro Diario** cuando:
- Necesites ver todas las transacciones cronológicamente
- Estés auditando movimientos
- Busques un asiento específico por fecha

### Usa el **Libro Mayor** cuando:
- Quieras ver el detalle de una cuenta específica
- Necesites analizar ingresos, gastos o cualquier cuenta
- Estés conciliando cuentas bancarias

### Usa el **Balance de Comprobación** cuando:
- Vayas a cerrar el mes
- Necesites verificar que todo cuadre
- Estés preparando estados financieros

### Usa el **Estado de Resultados** cuando:
- Quieras saber si ganaste o perdiste dinero
- Necesites tomar decisiones de precios o costos
- Vayas a presentar resultados a socios

### Usa el **Balance General** cuando:
- Necesites conocer la situación financiera total
- Solicites un crédito o inversión
- Presentes declaraciones tributarias anuales

---

## 📌 Resumen Visual

```
┌─────────────────────────────────────────────────────────┐
│                    REPORTES CONTABLES                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📖 Libro Diario      →  ¿Qué pasó cada día?           │
│  📗 Libro Mayor       →  ¿Cómo va cada cuenta?         │
│  ⚖️  Balance Comprobación → ¿Está todo cuadrado?        │
│  💰 Estado Resultados →  ¿Ganamos o perdimos?          │
│  📊 Balance General   →  ¿Cómo estamos hoy?            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🧠 Tip Final

> **La contabilidad cuenta una historia:**
> 
> - El **Libro Diario** es el día a día
> - El **Libro Mayor** es el historial de cada personaje (cuenta)
> - El **Balance de Comprobación** es el resumen del capítulo
> - El **Estado de Resultados** es si fue un buen o mal capítulo
> - El **Balance General** es cómo quedó todo al final del capítulo

---

📄 *Este módulo de reportes te permite generar todos estos informes automáticamente desde los datos registrados en Contabilidad.*
