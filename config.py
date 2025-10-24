# config.py
import os
import sys

# --------------------------
# CONFIGURATION
CSV_FILE = "meknes_prayer_times_2025.csv"
BACKGROUND_FILE = "background.jpg"
ADHAN_FILE = "adhan.wav"
IQAMA_FILE = "iqama.wav"
CITY = "Meknes"
COUNTRY = "Morocco"
REFRESH_INTERVAL_MS = 1000

# Buttons images
CLOSE_IMG = "close.png"
MINIMIZE_IMG = "minimize.png"

# Arabic labels
DISPLAY_NAMES = {
    "Fajr": "الفجر",
    "Dhuhr": "الظهر", 
    "Asr": "العصر",
    "Maghrib": "المغرب",
    "Isha": "العشاء"
}

MOSQUE_NAME = "مسجد موساوة صغير"
PLACE_NAME = "مدينة مكناس - المغرب"

# وقت الإقامة بعد الأذان (دقائق)
IQAMA_DELAY = {
    "Fajr": 19,
    "Dhuhr": 14,
    "Asr": 14,
    "Maghrib": 9,
    "Isha": 14
}

# ألوان الثيمات
THEME_COLORS = {
    "light": {
        "bg_color": "#b7d3d6",
        "text_color": "#2c3e50",
        "title": "#e74c3c",
        "accent_color": "#3498db",
        "prayer_bg": "#367a85",
        "prayer_border": "#bdc3c7",
        "countdown_color": "#ecf0f1",
        "schedule_bg": "#367a85",
        "column_bg": "#4A7BBA"
    },
    "dark": {
        "bg_color": "#1a1a1a", 
        "title": "gold",
        "text_color": "#ecf0f1",
        "accent_color": "#3498db",
        "prayer_bg": "#2C5282",
        "prayer_border": "#bdc3c7",
        "countdown_color": "#00FFFF",
        "schedule_bg": "#2C5282",
        "column_bg": "#4A7BBA"
    }
}

def resource_path(relative_path):
    """الحصول على المسار الصحيح للملفات"""
    try:
        base_path = sys._MEIPASS  # داخل EXE
    except Exception:
        base_path = os.path.abspath(".")  # وقت التشغيل من الكود العادي
    return os.path.join(base_path, relative_path)