import re
import pandas as pd
from PyPDF2 import PdfReader
from datetime import datetime

def convertir_fecha(fecha_texto):
    meses = {"ENE": "01", "FEB": "02", "MAR": "03", "ABR": "04", "MAY": "05", "JUN": "06",
             "JUL": "07", "AGO": "08", "SET": "09", "OCT": "10", "NOV": "11", "DIC": "12"}
    dia = fecha_texto[:2]
    mes_abrev = fecha_texto[2:5].upper()
    return f"2025-{meses.get(mes_abrev, '01')}-{dia}"

def parse_monto(valor):
    if not valor:
        return ""
    valor = valor.strip().replace(" ", "")
    if "," in valor and "." in valor:
        valor = valor.replace(",", "")
    elif "," in valor and "." not in valor:
        valor = valor.replace(",", ".")
    return float(valor)

def generar_comentario(desc):
    desc = desc.lower()
    if "haber" in desc:
        return "Depósito de sueldo"
    elif "adelanto" in desc:
        return "Adelanto de sueldo"
    elif "visa" in desc:
        return "Pago de tarjeta"
    elif "transf" in desc or "tran" in desc:
        return "Transferencia entre cuentas"
    elif "comis" in desc:
        return "Comisión por adelanto"
    elif "cargo" in desc:
        return "Descuento por adelanto"
    return "Movimiento bancario"

def extraer_movimientos_pdf(ruta_pdf):
    reader = PdfReader(ruta_pdf)
    texto_completo = "".join([p.extract_text() for p in reader.pages])
    lineas = texto_completo.split("\n")
    movimientos = []

    for linea in lineas:
        tokens = linea.strip().split()
        if len(tokens) >= 3 and re.match(r"\d{2}[A-Z]{3}", tokens[0]) and tokens[0] == tokens[1]:
            fecha = convertir_fecha(tokens[0])
            posibles_montos = [t for t in tokens if re.match(r"^[\d,\.]+$", t)]
            descripcion_tokens = [t for t in tokens[2:] if t not in posibles_montos]
            descripcion = " ".join(descripcion_tokens)

            cargo, abono = "", ""
            if len(posibles_montos) == 1:
                # Un solo monto → decidir si es abono o cargo según descripción
                if "haber" in descripcion.lower() or "adelanto" in descripcion.lower():
                    abono = parse_monto(posibles_montos[0])
                else:
                    cargo = parse_monto(posibles_montos[0])
            elif len(posibles_montos) == 2:
                cargo = parse_monto(posibles_montos[0])
                abono = parse_monto(posibles_montos[1])

            movimientos.append({
                "Fecha": fecha,
                "Descripción": descripcion,
                "Cargo": cargo,
                "Abono": abono,
                "Comentario": generar_comentario(descripcion)
            })

    return pd.DataFrame(movimientos)

# === Ejecutar ===
if __name__ == "__main__":
    ruta_pdf = "EECC-SUELDO.pdf"
    fecha_actual = datetime.now().strftime("%Y.%m.%d %H.%M")
    nombre_excel = f"EECC-SUELDO-{fecha_actual}.xlsx"

    df = extraer_movimientos_pdf(ruta_pdf)
    df.to_excel(nombre_excel, index=False)
    print(f"✅ Excel generado: {nombre_excel}")