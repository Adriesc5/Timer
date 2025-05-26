import os
from dotenv import load_dotenv
import sys

# Detecta si está empaquetado como .exe
if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
else:
    basedir = os.path.dirname(os.path.abspath(__file__))

dotenv_path = os.path.join(basedir, '.env')
load_dotenv(dotenv_path)

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

VALID_C = {
    "Tanking": ("Tan123!", "E2X"),
    "Meny": ("Bleach89", "E2X"),
    "Beto": ("Betorocks", "E2X"),
    "2": ("2", "MPU"),
    "JavierR": ("", ""),
    "1": ("1", "E2X"),
    "TanMP": ("TanMP1", "MPU"),
}