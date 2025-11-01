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

def load_csv():
    """تحميل بيانات CSV من الملف بالتنسيق المبسط"""
    csv_data = []
    place = PLACE_NAME
    
    try:
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                csv_data = list(reader)
                
                # استخراج المكان من أول سطر إذا كان موجوداً
                if csv_data and 'place' in csv_data[0]:
                    place = csv_data[0]['place']
                
                print(f"تم تحميل {len(csv_data)} يوم من ملف CSV")
                
                # طباعة أول سطر للتحقق من البيانات
                if csv_data:
                    print("مثال على البيانات المحملة:")
                    first_row = csv_data[0]
                    for key, value in first_row.items():
                        print(f"  {key}: {value}")
        else:
            print(f"ملف CSV غير موجود: {CSV_FILE}")
            
    except Exception as e:
        print(f"خطأ في قراءة ملف CSV: {e}")
    
    return csv_data, place

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
        'overlay_icon_font': max(140, int(130 * scale_factor)),
        'overlay_text_font': max(60, int(70 * scale_factor)),
        'overlay_countdown_font': max(80, int(75 * scale_factor)),
        'button_height': max(35, int(55 * scale_factor)),
        'next_prayer_width': max(400, int(500 * scale_factor)),
        'next_prayer_height': max(140, int(200 * scale_factor)),
        'schedule_height': max(140, int(200 * scale_factor)),
        'column_width': max(90, int(130 * scale_factor)),
        'column_height': max(70, int(100 * scale_factor)),
        'title_pady': max(2, int(10 * scale_factor)),
        'center_pady': max(8, int(15 * scale_factor)),
        'bottom_pady': max(15, int(25 * scale_factor)),
        'column_padx': max(6, int(10 * scale_factor))
    }