# 📘 Módulo de Contabilidad – Explicación General

Este módulo se encarga de llevar el **registro contable** de todas las operaciones financieras de la empresa.  
Está compuesto principalmente por **dos secciones:**  
1. 🧾 **Plan de Cuentas**  
2. 🧮 **Asientos Contables**

---

## 🧾 1. Plan de Cuentas

El **Plan de Cuentas** es una lista organizada con **todas las cuentas contables** que la empresa utiliza para clasificar el dinero y las operaciones.  
Cada cuenta tiene un **código**, un **nombre**, un **tipo** (activo, pasivo, ingreso, gasto, etc.) y una **naturaleza** (deudora o acreedora).

### 🔹 Ejemplo de cuentas

| Código | Nombre                  | Tipo     | Naturaleza |
|---------|--------------------------|-----------|-------------|
| 1105    | Caja                     | Activo    | Deudora     |
| 1110    | Bancos                   | Activo    | Deudora     |
| 1305    | Clientes                 | Activo    | Deudora     |
| 2105    | Proveedores              | Pasivo    | Acreedora   |
| 4105    | Ingresos por ventas      | Ingreso   | Acreedora   |
| 5105    | Gastos de administración | Gasto     | Deudora     |

📘 En palabras simples:  
El **Plan de Cuentas** es como un **diccionario contable**.  
Ahí se definen todas las “categorías” donde puede entrar o salir el dinero.

Ejemplo:
- Si pagas el arriendo → va a la cuenta “Gastos de arriendo”.  
- Si te entra plata por una venta → va a la cuenta “Ingresos por ventas”.

---

## 🧮 2. Asientos Contables

Los **Asientos Contables** son los **movimientos reales del dinero** entre las cuentas del plan.  
Cada vez que ocurre una operación (pago, cobro, egreso, compra, etc.), se genera un asiento que registra:

- Qué cuentas se afectan.  
- Cuánto se debita o acredita en cada una.  
- Una fecha y descripción del movimiento.

### 🔹 Ejemplo de asiento

| Cuenta | Descripción | Débito | Crédito |
|---------|--------------|--------|---------|
| 5120 | Gasto de servicios públicos | 200.000 | — |
| 1110 | Banco | — | 200.000 |

📘 En palabras simples:  
Un **asiento contable** muestra de **dónde salió** y **a dónde fue** el dinero.  
Es la forma en la que la contabilidad deja evidencia de cada operación.

---

## 💰 Diferencia entre Cuentas Bancarias, Plan de Cuentas y Asientos

| Concepto | Qué es | Ejemplo |
|-----------|--------|----------|
| **Cuentas Bancarias** | Son las cuentas reales del banco donde está el dinero. | Bancolombia, Davivienda, etc. |
| **Plan de Cuentas** | Es la lista general de todas las cuentas contables, no solo las bancarias. | Caja, banco, proveedores, ingresos, gastos... |
| **Asientos Contables** | Son los movimientos que se registran entre esas cuentas. | Pago, cobro, egreso, compra, etc. |

---

## 🧩 Relación entre los módulos

- **Tesorería** maneja el **dinero real** (pagos, cobros, egresos).  
- **Contabilidad** maneja los **registros contables** de esos movimientos.  
- Cada acción en tesorería puede generar automáticamente un **asiento contable** con las cuentas correspondientes del **Plan de Cuentas**.

---

## 🧠 En resumen

- **Plan de Cuentas:** Define las categorías donde se clasifica el dinero.  
- **Asientos Contables:** Registran los movimientos reales entre esas categorías.  
- **Cuentas Bancarias:** Son parte del plan, pero solo las que representan dinero en los bancos.

---

📄 **Ejemplo visual**

```text
Pago de luz por $200.000 desde la cuenta Bancolombia:

- Cuenta 5120 (Gastos de servicios públicos) → Débito 200.000
- Cuenta 1110 (Banco Bancolombia) → Crédito 200.000
