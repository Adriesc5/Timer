from dotenv import load_dotenv
import os

load_dotenv()  

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

VALID_C = {
    "Tanking": ("Tan123!", "E2X"),
    "Meny": ("Bleach89", "E2X"),
    "Beto": ("Betorocks", "E2X"),
    "LMV": ("Adri57", "MPU"),
    "JavierR": ("", ""),
    "1": ("1", "E2X")
}