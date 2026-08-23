import time
import threading
import requests
import flet as ft
from plyer import battery, gps

URL_SERVIDOR = "https://servidor-monitoreo.onrender.com/api/rastreo"  # Asegúrate de poner tu URL exacta de Render

# Variables globales para coordenadas
ultima_lat = "N/A"
ultima_lon = "N/A"

def on_location_change(**kwargs):
    global ultima_lat, ultima_lon
    ultima_lat = kwargs.get('lat', 'N/A')
    ultima_lon = kwargs.get('lon', 'N/A')

def inicializar_gps():
    try:
        gps.configure(on_location=on_location_change)
        gps.start(minTime=1000, minDistance=1)
    except Exception as e:
        print(f"No se pudo iniciar el GPS: {e}")

def detener_gps():
    try:
        gps.stop()
    except Exception:
        pass

def obtener_info_bateria():
    try:
        estado = battery.status
        if estado and estado.get('percentage') is not None:
            pct = estado['percentage']
            cargando = "⚡" if estado.get('isCharging') else ""
            return f"{pct}% {cargando}".strip()
    except Exception:
        pass
    return "Desconocido"

def bucle_monitoreo(switch_ref, texto_estado, page):
    inicializar_gps()
    
    while switch_ref.value:
        bateria_str = obtener_info_bateria()
        
        payload = {
            "dispositivo": "Android-Flet",
            "bateria": bateria_str,
            "latitud": str(ultima_lat),
            "longitud": str(ultima_lon)
        }

        try:
            requests.post(URL_SERVIDOR, json=payload, timeout=30)
            texto_estado.value = "Estado: Reporte enviado con éxito"
        except Exception as e:
            texto_estado.value = "Estado: Error de conexión"
        
        page.update()
        
        # Pausa de 60 segundos antes del siguiente envio
        for _ in range(60):
            if not switch_ref.value:
                break
            time.sleep(1)

    detener_gps()
    texto_estado.value = "Estado: Inactivo"
    page.update()

def main(page: ft.Page):
    page.title = "Monitoreo GPS"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    texto_estado = ft.Text("Estado: Inactivo", size=16)

    def al_cambiar_switch(e):
        if switch_rastreo.value:
            texto_estado.value = "Estado: Iniciando rastreo..."
            page.update()
            hilo = threading.Thread(target=bucle_monitoreo, args=(switch_rastreo, texto_estado, page), daemon=True)
            hilo.start()
        else:
            texto_estado.value = "Estado: Deteniendo..."
            page.update()

    switch_rastreo = ft.Switch(label="Rastrear", value=False, on_change=al_cambiar_switch)

    page.add(
        ft.Icon(name=ft.icons.LOCATION_ON, size=64, color=ft.colors.BLUE),
        switch_rastreo,
        texto_estado
    )

ft.app(target=main)