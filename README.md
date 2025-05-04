# Consolidación de EECC a Excel — README

## Descripción

Este script unifica los movimientos de tres estados de cuenta en PDF (**Ahorro, Sueldo, Crédito**) en un único archivo Excel compatible con tu plantilla de finanzas personales. Detecta las diferentes estructuras de cada PDF y exporta 12 columnas listas para automatización de formularios.

## Archivos esperados

```
📂 proyecto/
├── EECC-AHORRO.pdf
├── EECC-SUELDO.pdf
├── EECC-CREDITO.pdf
└── extract_eecc.py  # script principal
```

## Requisitos

| Herramienta | Versión recomendada |
| ----------- | ------------------- |
| Python      | 3.9 +               |
| pdfplumber  | ≥ 0.10              |
| pandas      | ≥ 2.0               |
| openpyxl    | ≥ 3.1               |

Instala todo de una vez:

```bash
pip install pdfplumber pandas openpyxl
```

## Uso rápido

```bash
python extract_eecc.py
```

Al finalizar verás algo como:

```
✅ 243 movimientos exportados a resultado_2025.05.15 15.33.xlsx
```

El Excel se genera en la misma carpeta.

## Columnas del Excel

| Columna           | Fuente / lógica                                                    |
| ----------------- | ------------------------------------------------------------------ |
| FechaHora         | Fecha del movimiento + `00:00` (hora fija)                         |
| Tipo              | Solo para **Crédito**: `Ingreso` si monto<0, `Gasto` si >0         |
| Importe           | Valor absoluto (sin signo; los ingresos se diferencian por `Tipo`) |
| Moneda            | `PEN` (puedes cambiarla)                                           |
| CuentaOrigen      | `Ahorro`, `Sueldo` o `Crédito` según el PDF                        |
| Resto de columnas | Vacías para que las completes o las llene otro script              |

## Personalización

* **Separador decimal/ miles**: la expresión regular `AMT_TAIL` reconoce `1,234.56-` y `-1234.56`. Ajusta si tu banco cambia el formato.
* **Mes en texto**: modifica el diccionario `MONTH` si tu estado usa abreviaturas diferentes (p. ej. `SET` → `SEP`).
* **Año**: la función `year_from_text()` busca el año en el encabezado (`.../25`). Si tu PDF lo escribe distinto, adapta la regex `YEAR_RE`.
* **Columnas extra**: añade tu lógica en la sección marcada `# --- mapeo a columnas destino ---`.

## Troubleshooting

| Mensaje                   | Causa probable                                   | Solución                                      |
| ------------------------- | ------------------------------------------------ | --------------------------------------------- |
| `⚠️ Falta EECC-…pdf`      | El archivo no está donde se espera               | Verifica nombres y ruta en `FILES`            |
| Exporta muy pocas filas   | La línea no coincide con `DATE_TOK` o `AMT_TAIL` | Imprime `line` en el bucle y ajusta las regex |
| Valor de monto incorrecto | Separador de miles/decimales distinto            | Ajusta el reemplazo de `','` y `'.'`          |

## Ejemplo de salida

```
| FechaHora           | Tipo    | Importe | Moneda | CuentaOrigen | … |
|---------------------|---------|---------|--------|--------------|---|
| 01/04/2025 00:00    | Gasto   |  145.50 | PEN    | Crédito      |   |
| 03/04/2025 00:00    | Ingreso |  200.00 | PEN    | Crédito      |   |
| 04/04/2025 00:00    |         |  500.00 | PEN    | Ahorro       |   |
```

## Licencia

Uso personal / académico.  Adapta o redistribuye libremente citando la fuente.
