#!/usr/bin/env python3
"""
extractor_carpeta_imagenes.py

Toma como input la ruta a una carpeta que contiene imágenes (jpg, png, etc.),
extrae texto con OCR en español usando Tesseract, parsea líneas con doble fecha
y genera un Excel con columnas: Fecha | Descripción | Cargo | Abono | Comentario.

Instalación de dependencias:
  pip install pytesseract pillow pandas openpyxl
  # Asegúrate de tener Tesseract + idioma español instalado en tu sistema.

Uso:
  python extractor_carpeta_imagenes.py /ruta/a/mi_carpeta_de_imagenes
"""

import os
import re
import glob
import argparse
import pandas as pd
import pytesseract
from PIL import Image
from datetime import datetime

def convertir_fecha(texto):
    """Convierte '01ABR' a '2025-04-01'."""
    meses = {
        "ENE":"01","FEB":"02","MAR":"03","ABR":"04","MAY":"05","JUN":"06",
        "JUL":"07","AGO":"08","SET":"09","OCT":"10","NOV":"11","DIC":"12"
    }
    dia = texto[:2]
    mes = meses.get(texto[2:5].upper(), "01")
    return f"2025-{mes}-{dia}"

def parse_monto(v):
    """Normaliza separadores y convierte a float."""
    if not v:
        return ""
    s = v.strip().replace(" ", "")
    if "," in s and "." in s:
        s = s.replace(",", "")
    elif "," in s and "." not in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return ""

def generar_comentario(desc):
    """Etiqueta básica según patrones en la descripción."""
    d = desc.lower()
    if "yape de" in d or "abon plin" in d:
        return "Ingreso por app"
    if "yape a" in d or d.startswith("plin-"):
        return "Gasto por app"
    if "tran.ctas.terc" in d:
        return "Abono por transferencia"
    if "tran.ctas.prop" in d:
        return "Transferencia interna"
    if "bbva" in d:
        return "Transferencia a BBVA"
    if "visa" in d:
        return "Pago de tarjeta"
    if "retiro" in d:
        return "Retiro en efectivo"
    if "spotify" in d or "cabify" in d:
        return "Gasto digital"
    if "itf" in d or "mant." in d:
        return "Gasto bancario"
    return "Otro movimiento"

def procesar_imagenes_de_carpeta(carpeta):
    """
    Lee todas las imágenes jpg, jpeg, png de la carpeta indicada
    y retorna un DataFrame con las transacciones extraídas.
    """
    extensiones = ("*.jpg", "*.jpeg", "*.png")
    rutas = []
    for ext in extensiones:
        rutas.extend(glob.glob(os.path.join(carpeta, ext)))
    rutas.sort()

    pattern_monto = re.compile(r"[\d]{1,3}(?:[.,]\d{3})*[.,]\d{2}")
    movimientos = []

    for ruta in rutas:
        texto = pytesseract.image_to_string(Image.open(ruta), lang="spa")
        for linea in texto.split("\n"):
            linea = linea.strip()
            if not re.match(r"^\d{2}[A-Z]{3}\s+\d{2}[A-Z]{3}", linea):
                continue
            raw_fecha = linea[:6]
            fecha = convertir_fecha(raw_fecha)
            resto = linea[12:].rstrip()
            montos = pattern_monto.findall(resto)
            if not montos:
                continue

            # Inicializar valores
            cargo = abono = ""
            if len(montos) == 2:
                cargo = parse_monto(montos[0])
                abono = parse_monto(montos[1])
                descr = resto.replace(montos[0], "").replace(montos[1], "").strip()
            else:
                monto = montos[0]
                idx = resto.rfind(monto)
                descr = resto[:idx].strip()
                if idx > len(resto) * 0.6:
                    abono = parse_monto(monto)
                else:
                    cargo = parse_monto(monto)

            movimientos.append({
                "Fecha": fecha,
                "Descripción": descr,
                "Cargo": cargo,
                "Abono": abono,
                "Comentario": generar_comentario(descr)
            })

    return pd.DataFrame(movimientos)

def main():
    parser = argparse.ArgumentParser(description="Extraer transacciones de imágenes OCR en carpeta")
    parser.add_argument("carpeta", help="Ruta a la carpeta con imágenes JPG/PNG")
    args = parser.parse_args()
    df = procesar_imagenes_de_carpeta(args.carpeta)
    ts = datetime.now().strftime("%Y.%m.%d %H.%M")
    nombre = f"EECC-AHORRO-{ts}.xlsx"
    df.to_excel(nombre, index=False)
    print(f"✅ Excel generado: {nombre}")

if __name__ == "__main__":
    main()
