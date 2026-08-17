import flet as ft
import requests
import time
import threading

# Se añade el endpoint /data a la URL de Render
URL_SERVIDOR = "https://servidor-monitoreo.onrender.com/data"

def main(page: ft.Page):
    page.title = "Agente de Monitoreo"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    estado_txt = ft.Text("Estado: Desconectado", size=20)
    rastreando = False
    
    def bucle_rastreo():
        nonlocal rastreando
        while rastreando:
            try:
                payload = {
                    "dispositivo": "Movil-Android",
                    "bateria": "OK"
                }
                requests.post(URL_SERVIDOR, json=payload, timeout=5)
                estado_txt.value = f"Último envío: {time.strftime('%H:%M:%S')}"
            except Exception as e:
                estado_txt.value = f"Error: {e}"
            page.update()
            time.sleep(15) # Envía el reporte cada 15 segundos
            
    def alternar_rastreo(e):
        nonlocal rastreando
        if btn_sw.value:
            if not rastreando: # Previene acumular hilos repetidos
                rastreando = True
                estado_txt.value = "Estado: Conectado"
                threading.Thread(target=bucle_rastreo, daemon=True).start()
        else:
            rastreando = False
            estado_txt.value = "Estado: Desconectado"
        page.update()
            
    btn_sw = ft.Switch(label="Rastrear", on_change=alternar_rastreo)
    
    page.add(
        ft.Icon(ft.Icons.LOCATION_ON, size=50, color=ft.Colors.BLUE),
        btn_sw,
        estado_txt
    )

if __name__ == "__main__":
    ft.app(target=main)