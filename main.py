import time
import socket
import threading
import requests
import flet as ft
from plyer import battery

URL_SERVIDOR = "https://servidor-monitoreo.onrender.com/api/rastreo"  # Asegúrate de poner tu URL exacta de Render

ultima_ip_reportada = None

def obtener_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"Error al obtener IP: {e}")
        return "Desconocida"
    
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
    global ultima_ip_reportada
    while switch_ref.value:
        ip_actual = obtener_ip()
        bateria_str = obtener_info_bateria()
        
        payload = {
            "dispositivo": "Android-Flet",
            "bateria": bateria_str,
            "ip": ip_actual
        }

        try:
            requests.post(URL_SERVIDOR, json=payload, timeout=30)
            texto_estado.value = "Estado: Reporte enviado con éxito"
            ultima_ip_reportada = ip_actual
        except Exception as e:
            texto_estado.value = "Estado: Error de conexión"
            
        page.update()
        
        for _ in range(60):
            if not switch_ref.value:
                break
            time.sleep(1)  # Espera 1 segundo antes de la siguiente iteración

    texto_estado.value = "Estado: inactivo"
    page.update()
    
def main(page: ft.Page):
    page.title = "ADB IP Agent"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    switch_ref = ft.Ref[ft.Switch]()
    texto_estado = ft.Text(value="Estado: inactivo", size=20)

    def al_cambiar_switch(e):
        if switch_agente.value:
            texto_estado.value = "Estado: Reportando..."
            page.update()
            hilo = threading.Thread(target=bucle_monitoreo, args=(switch_agente, texto_estado, page), daemon=True)
            hilo.start()
        else:
            texto_estado.value = "Estado: Deteniendo..."
            page.update()

    switch_agente = ft.Switch(label="Agente ADB IP", value=False, on_change=al_cambiar_switch)

    page.add(
        ft.Icon(icon=ft.Icons.WIFI_TETHERING, size=64, color=ft.Colors.BLUE),
        switch_agente,
        texto_estado
    )

ft.app(target=main)
