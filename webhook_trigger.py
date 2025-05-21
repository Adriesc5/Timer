# webhook_trigger.py
import requests
from datetime import datetime, timedelta

def send_alert(horno, job, start_time, remaining, webhook_url, tipo="registro", unidad=None, actual=None, horas_expuestas=None):
    payload = {
        "horno": str(horno),
        "job": str(job),
        "start_time": start_time.strftime("%Y-%m-%d %H:%M"),
        "remaining": int(float(remaining)),  # ✅ convertimos a INT
        "tipo": str(tipo),
        "unidad": str(unidad),
        "actual": actual.strftime("%Y-%m-%d %H:%M") if actual else "",
        "horas_expuestas": str(horas_expuestas) if horas_expuestas is not None else "0"  # ✅ como STRING
    }

    print("📦 Payload being sent:")
    for k, v in payload.items():
        print(f"  {k}: {v} ({type(v).__name__})")

    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        print("✅ Alert successfully sent to Power Automate.")
    except Exception as e:
        print(f"❌ Failed to send alert: {e}")
        print(f"❗ Server response: {response.text if 'response' in locals() else 'no response'}")
