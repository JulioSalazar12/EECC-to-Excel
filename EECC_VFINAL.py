# -*- coding: utf-8 -*-
"""
Consolida EECC‑AHORRO.pdf, EECC‑SUELDO.pdf y EECC‑CREDITO.pdf
en un Excel con 12 columnas predefinidas.
"""
import os, re, pdfplumber, pandas as pd
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
FILES = {
    os.path.join(BASE, 'EECC-AHORRO.pdf'):  'Ahorro',
    os.path.join(BASE, 'EECC-SUELDO.pdf'):  'Sueldo',
    os.path.join(BASE, 'EECC-CREDITO.pdf'): 'Crédito',
}

MONTH = {'ENE':'01','FEB':'02','MAR':'03','ABR':'04','MAY':'05','JUN':'06',
         'JUL':'07','AGO':'08','SEP':'09','OCT':'10','NOV':'11','DIC':'12'}
DATE_TOK = re.compile(r'^\s*(\d{1,2}[A-Za-z]{3})\s+(\d{1,2}[A-Za-z]{3})\s+(.*)$')
AMT_TAIL = re.compile(r'(-?\d[\d,]*\.\d{2}-?)\s*$')
YEAR_RE  = re.compile(r'\d{2}/\d{2}/(\d{2})')   # capta …/yy

def mes_a_num(tok: str) -> str|None:
    return MONTH.get(tok.upper(), None)

def to_fecha(tok: str, year: str) -> str|None:
    dd, mon = tok[:2].zfill(2), mes_a_num(tok[2:])
    return f'{dd}/{mon}/{year}' if mon else None

def year_from_text(txt: str) -> str:
    m = YEAR_RE.search(txt)
    return f'20{m.group(1)}' if m else str(datetime.now().year)

def extraer(path: str, cuenta: str) -> list[dict]:
    rows = []
    with pdfplumber.open(path) as pdf:
        anio = year_from_text(pdf.pages[0].extract_text() or '')
        for p in pdf.pages:
            for line in (p.extract_text() or '').split('\n'):
                if not (m := DATE_TOK.match(line)):
                    continue
                f_tok, _f2, resto = m.groups()
                fecha = to_fecha(f_tok, anio)
                if not fecha:
                    continue
                m2 = AMT_TAIL.search(resto)
                if not m2:
                    continue

                raw = m2.group(1)
                neg_final = raw.endswith('-')
                raw_num = raw.rstrip('-').replace(',', '')  # quita miles
                try:
                    monto = float(raw_num)
                    monto = -monto if neg_final else monto
                except ValueError:
                    continue

                # --- mapeo a columnas destino ---
                tipo = ''
                if cuenta == 'Crédito':
                    tipo = 'Ingreso' if monto < 0 else 'Gasto'
                # Para Ahorro/Sueldo dejamos Tipo vacío

                desc = re.sub(r'\s+', ' ', resto[:m2.start()].strip())

                rows.append({
                    'FechaHora'     : fecha + ' 00:00',    # sin hora en el estado
                    'Tipo'          : tipo,
                    'Importe'       : abs(monto),
                    'Moneda'        : 'PEN',
                    'CuentaOrigen'  : cuenta,
                    'CuentaDestino' : '',
                    'Categoría'     : '',
                    'Etiquetas'     : '',
                    'Nota'          : desc,
                    'Pagador'       : '',
                    'FormaPago'     : '',
                    'EstadoPago'    : '',
                })
    return rows

def main():
    all_rows = []
    for pdf, cuenta in FILES.items():
        if not os.path.exists(pdf):
            print(f'⚠️  Falta {os.path.basename(pdf)}')
            continue
        all_rows.extend(extraer(pdf, cuenta))

    cols = ["FechaHora","Tipo","Importe","Moneda","CuentaOrigen","CuentaDestino",
            "Categoría","Etiquetas","Nota","Pagador","FormaPago","EstadoPago"]
    df = pd.DataFrame(all_rows, columns=cols)

    # Guarda Excel con timestamp
    out = f'resultado_{datetime.now().strftime("%Y.%m.%d %H.%M")}.xlsx'
    df.to_excel(out, index=False)
    print(f'✅ {len(df)} movimientos exportados a {out}')

if __name__ == '__main__':
    main()
