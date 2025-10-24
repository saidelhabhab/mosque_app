# utils.py
import csv
import os
from PIL import Image, ImageDraw
from config import resource_path, PLACE_NAME, CSV_FILE

def create_mosque_icon():
    """إنشاء أيقونة المسجد إذا لم تكن موجودة"""
    icon_path = "mosque.ico"
    if not os.path.exists(icon_path):
        try:
            img = Image.new('RGB', (256, 256), color='#0A1F3A')
            draw = ImageDraw.Draw(img)
            
            # رسم قبة المسجد
            draw.ellipse([80, 50, 176, 146], fill='#FFD700', outline='#FFFFFF', width=3)
            
            # رسم قاعدة المسجد
            draw.rectangle([60, 120, 196, 200], fill='#2C5282', outline='#FFFFFF', width=2)
            
            # رسم باب المسجد
            draw.rectangle([115, 140, 141, 180], fill='#8B4513')
            
            img.save(icon_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            print(f"تم إنشاء الأيقونة: {icon_path}")
        except Exception as e:
            print(f"خطأ في إنشاء الأيقونة: {e}")

def load_csv(file_path=CSV_FILE):
    """تحميل بيانات أوقات الصلاة من ملف CSV"""
    data = {}
    place = PLACE_NAME
    
    # البحث عن الملف فمسارات مختلفة
    possible_paths = [
        file_path,
        resource_path(file_path),
        os.path.join(os.path.dirname(__file__), file_path),
        file_path
    ]
    
    csv_file_found = None
    for path in possible_paths:
        if os.path.exists(path):
            csv_file_found = path
            print(f"تم العثور على ملف CSV: {path}")
            break
    
    if not csv_file_found:
        print(f"تحذير: لم يتم العثور على ملف CSV")
        return data, place
    
    try:
        with open(csv_file_found, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                date = row.get("تاريخ") or row.get("date")
                if date:
                    data[date] = {
                        "Fajr": row.get("الفجر","") or row.get("Fajr",""),
                        "Dhuhr": row.get("الظهر","") or row.get("Dhuhr",""),
                        "Asr": row.get("العصر","") or row.get("Asr",""),
                        "Maghrib": row.get("المغرب","") or row.get("Maghrib",""),
                        "Isha": row.get("العشاء","") or row.get("Isha","")
                    }
                if "place" in row and row["place"]:
                    place = row["place"]
        print(f"تم تحميل {len(data)} يوم من ملف CSV")
    except Exception as e:
        print(f"خطأ في قراءة ملف CSV: {e}")
    
    return data, place

def calculate_font_scales(screen_width, screen_height):
    """حساب أحجام الخطوط والعناصر حسب دقة الشاشة"""
    screen_area = screen_width * screen_height
    diagonal = (screen_width**2 + screen_height**2)**0.5
    
    # حساب عامل التحجيم بناءً على المساحة والقطر
    if screen_area >= 16_000_000:  # 8K - TV 80 inch
        scale_factor = 3.2
        screen_type = "TV 80 بوصة"
    elif screen_area >= 8_000_000:  # 4K - TV 50-65 inch
        scale_factor = 2.4
        screen_type = "TV 50-65 بوصة"
    elif screen_area >= 4_000_000:  # QHD - TV 40 inch
        scale_factor = 1.8
        screen_type = "TV 40 بوصة"
    elif screen_area >= 2_000_000:  # Full HD - TV 32 inch
        scale_factor = 1.4
        screen_type = "TV 32 بوصة"
    elif screen_area >= 1_500_000:  # Laptop
        scale_factor = 1.1
        screen_type = "لابتوب"
    else:  # شاشات صغيرة
        scale_factor = 0.9
        screen_type = "شاشة صغيرة"
        
    print(f"نوع الشاشة: {screen_type}")
    print(f"المساحة: {screen_area:,} بيكسل")
    print(f"القطر: {diagonal:.0f} بيكسل")
    print(f"عامل التحجيم: {scale_factor:.1f}")
    
    return {
        'scale_factor': scale_factor,
        'screen_type': screen_type,
        'mosque_font': max(35, int(50 * scale_factor)),
        'place_font': max(25, int(40 * scale_factor)),
        'date_font': max(20, int(35 * scale_factor)),
        'next_title_font': max(25, int(40 * scale_factor)),
        'next_name_font': max(30, int(50 * scale_factor)),
        'countdown_font': max(25, int(42 * scale_factor)),
        'schedule_title_font': max(25, int(40 * scale_factor)),
        'prayer_name_font': max(18, int(28 * scale_factor)),
        'prayer_time_font': max(16, int(25 * scale_factor)),
        'overlay_icon_font': max(70, int(110 * scale_factor)),
        'overlay_text_font': max(40, int(60 * scale_factor)),
        'overlay_countdown_font': max(45, int(65 * scale_factor)),
        'button_height': max(35, int(55 * scale_factor)),
        'next_prayer_width': max(450, int(650 * scale_factor)),
        'next_prayer_height': max(160, int(220 * scale_factor)),
        'schedule_height': max(140, int(200 * scale_factor)),
        'column_width': max(90, int(130 * scale_factor)),
        'column_height': max(70, int(100 * scale_factor)),
        'title_pady': max(8, int(15 * scale_factor)),
        'center_pady': max(8, int(15 * scale_factor)),
        'bottom_pady': max(15, int(25 * scale_factor)),
        'column_padx': max(6, int(10 * scale_factor))
    }