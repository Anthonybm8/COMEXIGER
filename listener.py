import keyboard
import requests
import re
from datetime import datetime

BUFFER = ""

API_URL = "http://localhost:8000/api/rendimientos/"

def procesar_qr(texto):
    # Ejemplo recibido:
    # IDÑ5FFC3B94 ] MesaÑ2 ] FlorÑFreddon ] MedidaÑ50 ] FechaÑ22-11-2025

    partes = texto.split(" ] ")

    datos = {}
    for parte in partes:
        if "IDÑ" in parte:
            datos["codigo_id"] = parte.replace("IDÑ", "").strip()
        if "MesaÑ" in parte:
            datos["numero_mesa"] = parte.replace("MesaÑ", "").strip()
        if "FlorÑ" in parte:
            datos["variedad"] = parte.replace("FlorÑ", "").strip()
        if "MedidaÑ" in parte:
            datos["medida"] = parte.replace("MedidaÑ", "").strip()
        if "FechaÑ" in parte:
            fecha_txt = parte.replace("FechaÑ", "").strip()
            datos["fecha_entrada"] = datetime.strptime(fecha_txt, "%d-%m-%Y")

    return datos

def enviar_api(datos):
    payload = {
        "codigo_id": datos["codigo_id"],
        "numero_mesa": datos["numero_mesa"],
        "variedad": datos["variedad"],
        "medida": datos["medida"],
        "bonches": 1,
        "fecha_entrada": datos["fecha_entrada"].isoformat(),
        "fecha_salida": None
    }

    try:
        r = requests.post(API_URL, json=payload)
        print("Respuesta API:", r.status_code, r.text)
    except Exception as e:
        print("ERROR enviando API:", e)


def on_key(event):
    global BUFFER

    if event.name == "enter":
        texto = BUFFER.strip()
        BUFFER = ""
        if texto:
            datos = procesar_qr(texto)
            enviar_api(datos)
    else:
        if len(event.name) == 1:
            BUFFER += event.name
        elif event.name == "space":
            BUFFER += " "

keyboard.on_press(on_key)
keyboard.wait()
