import os
import sys


def resource_path(relative_path):
    """إرجاع المسار الصحيح للملفات سواء داخل PyInstaller أو في التطوير"""
    try:
        base_path = sys._MEIPASS  # داخل .exe
    except Exception:
        base_path = os.path.abspath(".")  # أثناء التطوير

    return os.path.join(base_path, relative_path)

# --------------------------
# CONFIGURATION
# --------------------------
# CONFIGURATION
CSV_FILE = resource_path("meknes_prayer_all.csv")
PRAYER_TIMES_CSV = resource_path("meknes_prayer_all.csv")
BACKGROUND_FILE = resource_path("background.jpg")
ADHAN_FILE = resource_path("adhan.wav")
IQAMA_FILE = resource_path("iqama.wav")
CLOSE_IMG = resource_path("close.png")
MINIMIZE_IMG = resource_path("minimize.png")
MOSQUE_ICON = resource_path("mosque.ico")

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

MOSQUE_NAME = "مسجد موساوة كبير"
PLACE_NAME = "مدينة مكناس - المغرب"

# وقت الإقامة بعد الأذان (دقائق)
IQAMA_DELAY = {
    "Fajr": 19,
    "Dhuhr": 14,
    "jomo3a_Dhuhr": 17,  # 1 دقيقة فقط للجمعة
    "Asr": 14,
    "Maghrib": 9,
    "Isha": 14
}

# أوقات الجمعة الخاصة
JUMA_SCHEDULE = {
    "khotba_duration": 15,  # 15 دقيقة مدة الخطبة
    "prayer_duration": 30,  # 30 ثانية مدة الصلاة
    "azkar_delay": 5 * 60   # 5 دقائق بعد الصلاة للأذكار
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
        "bg_color": "#b7d3d6",
        "text_color": "#2c3e50",
        "title": "#e74c3c",
        "accent_color": "#3498db",
        "prayer_bg": "#367a85",
        "prayer_border": "#bdc3c7",
        "countdown_color": "#ecf0f1",
        "schedule_bg": "#367a85",
        "column_bg": "#4A7BBA"
    }
}

