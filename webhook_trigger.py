# webhook_trigger.py
import requests
from datetime import datetime, timedelta

def send_alert(horno, job, start_time, remaining_seconds, webhook_url, tipo="advertencia",unidad=None):
    hrs, rem = divmod(remaining_seconds, 3600)
    mins, secs = divmod(rem, 60)
    remaining_str = f"{hrs:02}:{mins:02}:{secs:02}"

    payload = {
        "horno": horno,
        "job": job,
        "inicio": start_time.strftime("%Y-%m-%d %H:%M"),
        "tiempo_restante": remaining_str,
        "tipo": tipo,
        "unidad": unidad
    }

    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        print("✅ Alert successfully sent to Power Automate.")
    except Exception as e:
        print(f"❌ Failed to send alert: {e}")
