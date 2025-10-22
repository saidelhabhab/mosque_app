import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
import datetime, csv, os, threading, sys
from playsound import playsound
import os

if sys.stdout is not None:
    sys.stdout.reconfigure(encoding='utf-8')
# --------------------------
# CONFIGURATION
CSV_FILE = "meknes_prayer_times_2025.csv"
BACKGROUND_FILE = "background.jpg"
ADHAN_FILE = "adhan.wav"
IQAMA_FILE = "iqama.wav"  # ملف إقامة الصلاة
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

MOSQUE_NAME = "مسجد "
PLACE_NAME = "مدينة مكناس - المغرب"

# وقت الإقامة بعد الأذان (دقائق) - أوقات مختلفة لكل صلاة
IQAMA_DELAY = {
    "Fajr": 19,
    "Dhuhr": 14,
    "Asr": 14,
    "Maghrib": 4,
    "Isha": 14
}

# --------------------------
# CustomTkinter Settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # داخل EXE
    except Exception:
        base_path = os.path.abspath(".")  # وقت التشغيل من الكود العادي
    return os.path.join(base_path, relative_path)

def create_mosque_icon():
    """إنشاء أيقونة المسجد إذا لم تكن موجودة"""
    icon_path = "mosque.ico"
    if not os.path.exists(icon_path):
        try:
            # إنشاء صورة بسيطة للمسجد
            img = Image.new('RGB', (256, 256), color='#0A1F3A')
            draw = ImageDraw.Draw(img)
            
            # رسم قبة المسجد (دائرة)
            draw.ellipse([80, 50, 176, 146], fill='#FFD700', outline='#FFFFFF', width=3)
            
            # رسم قاعدة المسجد
            draw.rectangle([60, 120, 196, 200], fill='#2C5282', outline='#FFFFFF', width=2)
            
            # رسم باب المسجد
            draw.rectangle([115, 140, 141, 180], fill='#8B4513')
            
            # حفظ كأيقونة
            img.save(icon_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            print(f"تم إنشاء الأيقونة: {icon_path}")
        except Exception as e:
            print(f"خطأ في إنشاء الأيقونة: {e}")

def load_csv(file_path=CSV_FILE):
    data = {}
    place = PLACE_NAME
    
    # البحث عن الملف فمسارات مختلفة
    possible_paths = [
        file_path,  # المسار الأصلي
        resource_path(file_path),  # داخل EXE
        os.path.join(os.path.dirname(__file__), file_path),  # مسار الكود
        file_path  # المسار الحالي
    ]
    
    csv_file_found = None
    for path in possible_paths:
        if os.path.exists(path):
            csv_file_found = path
            print(f"تم العثور على ملف CSV: {path}")
            break
    
    if not csv_file_found:
        print(f"تحذير: لم يتم العثور على ملف CSV في أي من المسارات التالية:")
        for path in possible_paths:
            print(f"  - {path}")
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

# --------------------------
class MosqueApp:
    def __init__(self, root):
        self.root = root
        self.root.title(MOSQUE_NAME)
        # إنشاء الأيقونة إذا لم تكن موجودة
        create_mosque_icon()
        
         # إضافة الأيقونة للتطبيق
        try:
            # جرب تلقى الأيقونة فمسارات مختلفة
            icon_paths = [
                "mosque.ico",
                resource_path("mosque.ico"),
                "icon.ico", 
                resource_path("icon.ico"),
                os.path.join(os.path.dirname(__file__), "mosque.ico")
            ]
            
            icon_found = None
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    icon_found = icon_path
                    print(f"تم العثور على الأيقونة: {icon_path}")
                    break
            
            if icon_found:
                self.root.iconbitmap(icon_found)
                print("تم تعيين أيقونة التطبيق بنجاح")
            else:
                print("تحذير: لم يتم العثور على أيقونة التطبيق")
        except Exception as e:
            print(f"خطأ في تحميل الأيقونة: {e}")
            
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda e: self.toggle_fullscreen())
        self.root.bind("<F1>", lambda e: self.test_adhan_maghrib())  # Test Adhan F1

        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        
         
        
        # تحديد حجم الخطوط حسب دقة الشاشة
        self.font_scales = self.calculate_font_scales(screen_w, screen_h)

        # Background setup - خلفية التطبيق
        bg_file = resource_path(BACKGROUND_FILE)
        if os.path.exists(bg_file):
            try:
                bg_img = Image.open(bg_file)
                self.bg_image = ctk.CTkImage(
                    light_image=bg_img,
                    dark_image=bg_img,
                    size=(screen_w, screen_h)
                )
                self.bg_label = ctk.CTkLabel(root, image=self.bg_image, text="")
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            except Exception as e:
                print(f"Error loading background: {e}")
                # خلفية زرقاء داكنة
                gradient_color = "#0A1F3A"
                self.bg_label = ctk.CTkLabel(root, text="", fg_color=gradient_color)
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            print(f"Background file not found: {bg_file}")
            # خلفية زرقاء داكنة
            gradient_color = "#0A1F3A"
            self.bg_label = ctk.CTkLabel(root, text="", fg_color=gradient_color)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Main container فوق الخلفية (باش العناصر تبان مزيان)
        main_container = ctk.CTkFrame(root, fg_color="transparent")
        main_container.pack(fill="both", expand=True)

        # Top buttons - إصلاح مشكل الأيقونات
        btn_frame = ctk.CTkFrame(main_container, fg_color="transparent", height=self.font_scales['button_height'])
        btn_frame.pack(side="top", fill="x", padx=20, pady=10)
        btn_frame.pack_propagate(False)

        # Close and minimize buttons - استخدام CTkImage للأيقونات
        button_container = ctk.CTkFrame(btn_frame, fg_color="transparent")
        button_container.pack(side="right")

        # زر الإغلاق مع صورة
        close_img_path = resource_path(CLOSE_IMG)
        if os.path.exists(close_img_path):
            try:
                close_img = Image.open(close_img_path)
                self.close_icon = ctk.CTkImage(
                    light_image=close_img,
                    dark_image=close_img,
                    size=(20, 20)
                )
                close_btn = ctk.CTkButton(
                    button_container,
                    image=self.close_icon,
                    text="",  # نص فارغ
                    width=30,
                    height=30,
                    fg_color="#E74C3C",
                    hover_color="#C0392B",
                    command=root.destroy
                )
            except Exception as e:
                print(f"Error loading close icon: {e}")
                close_btn = ctk.CTkButton(
                    button_container,
                    text="X",
                    width=30,
                    height=30,
                    fg_color="#E74C3C",
                    hover_color="#C0392B",
                    font=("Arial", 16, "bold"),
                    command=root.destroy
                )
        else:
            print(f"Close icon not found: {close_img_path}")
            close_btn = ctk.CTkButton(
                button_container,
                text="X",
                width=30,
                height=30,
                fg_color="#E74C3C",
                hover_color="#C0392B",
                font=("Arial", 16, "bold"),
                command=root.destroy
            )
        
        close_btn.pack(side="right", padx=5)

        # زر التصغير مع صورة
        minimize_img_path = resource_path(MINIMIZE_IMG)
        if os.path.exists(minimize_img_path):
            try:
                minimize_img = Image.open(minimize_img_path)
                self.minimize_icon = ctk.CTkImage(
                    light_image=minimize_img,
                    dark_image=minimize_img,
                    size=(20, 20)
                )
                min_btn = ctk.CTkButton(
                    button_container,
                    image=self.minimize_icon,
                    text="",  # نص فارغ
                    width=30,
                    height=30,
                    fg_color="#3498DB",
                    hover_color="#2980B9",
                    command=root.iconify
                )
            except Exception as e:
                print(f"Error loading minimize icon: {e}")
                min_btn = ctk.CTkButton(
                    button_container,
                    text="_",
                    width=30,
                    height=30,
                    fg_color="#3498DB",
                    hover_color="#2980B9",
                    font=("Arial", 16, "bold"),
                    command=root.iconify
                )
        else:
            print(f"Minimize icon not found: {minimize_img_path}")
            min_btn = ctk.CTkButton(
                button_container,
                text="_",
                width=30,
                height=30,
                fg_color="#3498DB",
                hover_color="#2980B9",
                font=("Arial", 16, "bold"),
                command=root.iconify
            )
        
        min_btn.pack(side="right", padx=5)

        # Mosque & place labels
        self.mosque_label = ctk.CTkLabel(
            main_container,
            text=MOSQUE_NAME,
            font=("Arial", self.font_scales['mosque_font'], "bold"),
            text_color="gold",  # أزرق فاتح
            fg_color="transparent"
        )
        self.mosque_label.pack(pady=(20, 5))

        self.place_label = ctk.CTkLabel(
            main_container,
            text=PLACE_NAME,
            font=("Arial", self.font_scales['place_font']),
            text_color="#B0E0E6",  
            fg_color="transparent"
        )
        self.place_label.pack(pady=(10, 2))

        # Date & Day
        self.date_label = ctk.CTkLabel(
            main_container,
            text="",
            font=("Arial", self.font_scales['date_font']),
            text_color="#E6F3FF",  # أزرق فاتح جداً
            fg_color="transparent"
        )
        self.date_label.pack(pady=(0, 5))

        # Next prayer section - في وسط الصفحة
        next_prayer_frame = ctk.CTkFrame(
            main_container,
            fg_color="#1E3A5F",  # أزرق داكن
            corner_radius=20,
            width=self.font_scales['next_prayer_width'],
            height=self.font_scales['next_prayer_height']
        )
        next_prayer_frame.pack(pady=20, expand=True)
        next_prayer_frame.pack_propagate(False)

        next_prayer_container = ctk.CTkFrame(next_prayer_frame, fg_color="transparent")
        next_prayer_container.pack(expand=True, fill="both")

        self.next_title = ctk.CTkLabel(
            next_prayer_container,
            text="الصلاة القادمة",
            font=("Arial", self.font_scales['next_title_font'], "bold"),
            text_color="gold"  
        )
        self.next_title.pack(pady=(20, 5))

        self.next_name = ctk.CTkLabel(
            next_prayer_container,
            text="",
            font=("Arial", self.font_scales['next_name_font'], "bold"),
            text_color="white"
        )
        self.next_name.pack(pady=10)

        self.countdown = ctk.CTkLabel(
            next_prayer_container,
            text="",
            font=("Arial", self.font_scales['countdown_font']),
            text_color="#00FFFF"  # أزرق سماوي
        )
        self.countdown.pack(pady=(5, 15))

        # Schedule - MODERN COLUMNS DESIGN
        schedule_frame = ctk.CTkFrame(
            main_container,
            fg_color="#2C5282",  # أزرق متوسط
            corner_radius=25,
            height=self.font_scales['schedule_height']
        )
        schedule_frame.pack(side="bottom", pady=30, padx=50, fill="x")
        schedule_frame.pack_propagate(False)

        # Title
        schedule_title = ctk.CTkLabel(
            schedule_frame,
            text="أوقات الصلاة اليوم",
            font=("Arial", self.font_scales['schedule_title_font'], "bold"),
            text_color="white"
        )
        schedule_title.pack(pady=15)

        # Prayer times in modern columns - ترتيب من اليمين لليسار
        columns_container = ctk.CTkFrame(schedule_frame, fg_color="transparent")
        columns_container.pack(pady=10)

        self.prayer_columns = []
        prayers = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]

        for i, prayer in enumerate(prayers):
            # حساب العمود المعاكس (من اليمين لليسار)
            reverse_i = len(prayers) - 1 - i
            
            column_frame = ctk.CTkFrame(
                columns_container,
                width=self.font_scales['column_width'],
                height=self.font_scales['column_height'],
                fg_color="#4A7BBA",  # أزرق
                corner_radius=15,
                border_width=2,
                border_color="#63B3ED"
            )
            column_frame.grid(row=0, column=reverse_i, padx=12, pady=5)
            column_frame.grid_propagate(False)
            column_frame.pack_propagate(False)
            
            # Prayer name
            name_label = ctk.CTkLabel(
                column_frame,
                text=DISPLAY_NAMES[prayer],
                font=("Arial", self.font_scales['prayer_name_font'], "bold"),
                text_color="#FFD700"  # ذهبي
            )
            name_label.pack(pady=(15, 5))
            
            # Prayer time
            time_label = ctk.CTkLabel(
                column_frame,
                text="--:--",
                font=("Arial", self.font_scales['prayer_time_font'], "bold"),
                text_color="white"
            )
            time_label.pack(pady=(5, 15))
            
            self.prayer_columns.append((prayer, time_label))

        # Overlay Adhan + Iqama
        self.overlay = ctk.CTkFrame(root, fg_color="#0A1F3A")  # خلفية زرقاء داكنة
        self.overlay.place(relwidth=1, relheight=1)
        
        overlay_container = ctk.CTkFrame(self.overlay, fg_color="transparent")
        overlay_container.pack(expand=True)
        
        # أيقونة متحركة للإقامة
        self.iqama_icon = ctk.CTkLabel(
            overlay_container,
            text="",
            font=("Arial", self.font_scales['overlay_icon_font'], "bold"),
            text_color="gold" 
        )
        self.iqama_icon.pack(pady=20)
        
        self.overlay_label = ctk.CTkLabel(
            overlay_container,
            text="",
            font=("Arial", self.font_scales['overlay_text_font'], "bold"),
            text_color="gold"  
        )
        self.overlay_label.pack(pady=10)
        
        self.overlay_countdown = ctk.CTkLabel(
            overlay_container,
            text="",
            font=("Arial", self.font_scales['overlay_countdown_font'], "bold"),
            text_color="#00FFFF"  # أزرق سماوي
        )
        self.overlay_countdown.pack(pady=10)
        
        self.overlay.lower()

        # Load CSV
        self.data, self.place = load_csv()
        self.current_date = datetime.date.today()
        self.last_adhan_played = None
        self.last_iqama_played = None
        self.iqama_scheduled = False
        self.current_prayer_for_iqama = None
        self.iqama_countdown_time = 0
        self.animation_running = False

        self.update_display()
        self.root.after(REFRESH_INTERVAL_MS, self.tick)

    def calculate_font_scales(self, screen_width, screen_height):
        """حساب أحجام الخطوط والعناصر حسب دقة الشاشة"""
        # تحديد نوع الشاشة حسب الدقة
        if screen_width >= 3840:  # TV 50 inch أو أكبر
            scale_factor = 1.8
        elif screen_width >= 1920:  # TV 40 inch
            scale_factor = 1.4
        else:  # TV 32 inch أو أصغر
            scale_factor = 1.0
            
        return {
            'mosque_font': int(55 * scale_factor),
            'place_font': int(45 * scale_factor),
            'date_font': int(40 * scale_factor),
            'next_title_font': int(45 * scale_factor),
            'next_name_font': int(55 * scale_factor),
            'countdown_font': int(48 * scale_factor),
            'schedule_title_font': int(45 * scale_factor),
            'prayer_name_font': int(30 * scale_factor),
            'prayer_time_font': int(28 * scale_factor),
            'overlay_icon_font': int(120 * scale_factor),
            'overlay_text_font': int(64 * scale_factor),
            'overlay_countdown_font': int(72 * scale_factor),
            'button_height': int(60 * scale_factor),
            'next_prayer_width': int(700 * scale_factor),
            'next_prayer_height': int(250 * scale_factor),
            'schedule_height': int(220 * scale_factor),
            'column_width': int(140 * scale_factor),
            'column_height': int(110 * scale_factor)
        }

    # --------------------------
    def toggle_fullscreen(self):
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))

    # --------------------------
    def find_next_prayer(self):
        """إيجاد الصلاة القادمة (يشمل فجر الغد بعد العشاء) حسب اليوم والشهر فقط"""
        now = datetime.datetime.now()
        today_str = now.strftime("%m-%d")  # فقط الشهر واليوم

        # البحث عن اليوم الحالي فـCSV
        day = None
        for date, times in self.data.items():
            if date[5:] == today_str:  # IGNORE YYYY
                day = times
                break

        if not day:
            return None, None

        base = datetime.datetime.combine(now.date(), datetime.time(0, 0))

        for key in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
            t = day.get(key)
            if not t:
                continue
            h, m = map(int, t.split(":"))
            dt = base + datetime.timedelta(hours=h, minutes=m)
            if dt > now:
                return key, dt

        # إذا مرّت كل الصلوات اليوم، خذ فجر الغد بنفس اليوم والشهر (السنة تتكرر)
        tomorrow = now + datetime.timedelta(days=1)
        tomorrow_str = tomorrow.strftime("%m-%d")

        next_day = None
        for date, times in self.data.items():
            if date[5:] == tomorrow_str:
                next_day = times
                break

        if next_day and "Fajr" in next_day and next_day["Fajr"]:
            h, m = map(int, next_day["Fajr"].split(":"))
            dt = datetime.datetime.combine(tomorrow.date(), datetime.time(h, m))
            return "Fajr", dt

        return None, None

    def play_adhan(self):
        adhan_file = resource_path(ADHAN_FILE)
        if os.path.exists(adhan_file):
            threading.Thread(target=lambda: playsound(adhan_file, block=True), daemon=True).start()

    def play_iqama(self):
        iqama_file = resource_path(IQAMA_FILE)
        if os.path.exists(iqama_file):
            threading.Thread(target=lambda: playsound(iqama_file, block=True), daemon=True).start()

    def test_adhan_maghrib(self):
        """اختبار الأذان للمغرب"""
        self.start_adhan_overlay("Maghrib")

    # --------------------------
    def start_adhan_overlay(self, prayer_name):
        """عرض شاشة الأذان"""
        print(f"بدأ الأذان لصلاة {prayer_name}")
        self.overlay_label.configure(text=f"🕌 أذان {DISPLAY_NAMES[prayer_name]} ")
        self.iqama_icon.configure(text="", font=("Arial", self.font_scales['overlay_icon_font'], "bold"))
        self.overlay_countdown.configure(text="")
        self.overlay.lift()
        
        # تشغيل الأذان
        self.play_adhan()
        
        # حفظ الصلاة الحالية للإقامة
        self.current_prayer_for_iqama = prayer_name
        
        # حساب وقت الإقامة بناءً على نوع الصلاة
        iqama_delay_minutes = IQAMA_DELAY.get(prayer_name, 1)
        print(f"سيتم الإقامة بعد {iqama_delay_minutes} دقائق")
        
        # إخفاء شاشة الأذان بعد دقيقة واحدة وبدء شاشة الإقامة
        self.root.after(60 * 1000, lambda: self.start_iqama_countdown(prayer_name, iqama_delay_minutes))

    # --------------------------
    def start_iqama_countdown(self, prayer_name, total_minutes):
        """بدء العد التنازلي للإقامة"""
        print(f"بدأ العد التنازلي للإقامة: {total_minutes} دقائق")

        self.current_prayer_for_iqama = prayer_name
        self.iqama_countdown_time = total_minutes * 60  # تحويل الدقائق إلى ثواني

        # تنظيف الشاشة القديمة
        self.overlay.lift()
        for widget in self.overlay.winfo_children():
            widget.destroy()

        # 🔹 الأيقونة المتحركة في الوسط
        self.iqama_icon = ctk.CTkLabel(
            self.overlay,
            text="🕌",
            font=("Arial", self.font_scales['overlay_icon_font'], "bold"),
            text_color="gold"
        )
        self.iqama_icon.place(relx=0.5, rely=0.35, anchor="center")

        # 🔹 Frame خاص بالنص والعداد تحت الأيقونة بمسافة كبيرة
        text_frame = ctk.CTkFrame(self.overlay, fg_color="#0A1F3A")
        text_frame.place(relx=0.5, rely=0.7, anchor="center")

        # النص الثابت
        self.iqama_text = ctk.CTkLabel(
            text_frame,
            text=f"إقامة صلاة {DISPLAY_NAMES[prayer_name]}",
            font=("Arial", self.font_scales['overlay_text_font'], "bold"),
            text_color="white"
        )
        self.iqama_text.pack(pady=(0, 15))

        # العد التنازلي الكبير
        self.overlay_countdown = ctk.CTkLabel(
            text_frame,
            text="",
            font=("Arial", self.font_scales['overlay_countdown_font'], "bold"),
            text_color="#00FFFF"
        )
        self.overlay_countdown.pack()

        # بدء التحريك والعد التنازلي
        self.animation_running = True
        self.animate_iqama_icon()
        self.update_iqama_countdown()

    # --------------------------
    def animate_iqama_icon(self, size=None, growing=True):
        """تحريك أيقونة الإقامة فقط (تكبير وتصغير دون التأثير على النصوص)"""
        if not self.animation_running:
            return

        if size is None:
            size = self.font_scales['overlay_icon_font']

        if growing:
            size += 8
            if size >= self.font_scales['overlay_icon_font'] + 30:
                growing = False
        else:
            size -= 8
            if size <= self.font_scales['overlay_icon_font'] - 20:
                growing = True

        if hasattr(self, "iqama_icon") and self.iqama_icon.winfo_exists():
            self.iqama_icon.configure(font=("Arial", size, "bold"))

        if self.overlay.winfo_ismapped() and self.animation_running:
            self.root.after(200, lambda: self.animate_iqama_icon(size, growing))

    # --------------------------
    def start_animation(self):
        """بدء تحريك الأيقونة"""
        self.animation_running = True
        self.animate_iqama_icon()

    # --------------------------
    def stop_animation(self):
        """إيقاف تحريك الأيقونة"""
        self.animation_running = False
        if hasattr(self, "iqama_icon") and self.iqama_icon.winfo_exists():
            self.iqama_icon.configure(font=("Arial", self.font_scales['overlay_icon_font'], "bold"))

    # --------------------------
    def play_iqama_sound(self):
        """تشغيل صوت الإقامة بعد انتهاء العد التنازلي"""
        if self.current_prayer_for_iqama:
            print(f"تشغيل صوت الإقامة لصلاة {self.current_prayer_for_iqama}")
            
            self.stop_animation()
            self.play_iqama()
            
            self.overlay_countdown.configure(text="إطفئ الهاتف")
            
            self.root.after(15 * 1000, self.hide_overlay)
            self.iqama_scheduled = False
            self.current_prayer_for_iqama = None

    # --------------------------
    def update_iqama_countdown(self):
        """تحديث العد التنازلي للإقامة"""
        if self.iqama_countdown_time > 0:
            minutes = self.iqama_countdown_time // 60
            seconds = self.iqama_countdown_time % 60
            
            # عرض العد التنازلي بشكل كبير
            self.overlay_countdown.configure(text=f"{minutes:02d}:{seconds:02d}")
            
            self.iqama_countdown_time -= 1
            self.root.after(1000, self.update_iqama_countdown)
        else:
            # انتهى العد التنازلي، تشغيل صوت الإقامة
            self.play_iqama_sound()

    # --------------------------
    def hide_overlay(self):
        """إخفاء الـ overlay"""
        self.overlay.lower()
        self.stop_animation()

    # --------------------------
    def update_next_prayer(self):
        key, dt = self.find_next_prayer()
        if key and dt:
            self.next_name.configure(text=DISPLAY_NAMES[key])
            remaining = dt - datetime.datetime.now()
            total = int(remaining.total_seconds())
            if total < 0: total = 0
            h = total//3600
            m = (total%3600)//60
            s = total%60
            
            # إذا كان باقي أقل من ساعة، عرض الدقائق والثواني فقط
            if h > 0:
                self.countdown.configure(text=f"باقي : {h:02d}:{m:02d}:{s:02d}")
            else:
                self.countdown.configure(text=f"باقي : {m:02d}:{s:02d}")

            if total <= 1 and self.last_adhan_played != key:
                self.last_adhan_played = key
                self.start_adhan_overlay(key)
        else:
            self.next_name.configure(text="--")
            self.countdown.configure(text="")

    # --------------------------
    def update_display(self):
        now = datetime.datetime.now()
        weekday_ar = ["الاثنين","الثلاثاء","الأربعاء","الخميس","الجمعة","السبت","الأحد"]
        self.date_label.configure(text=f"{weekday_ar[now.weekday()]}، {now.day} / {now.month} / {now.year} - {now.strftime('%H:%M:%S')}")
        
        # Use MM-DD for lookup
        today_str = now.strftime("%m-%d")
        day = None
        for date, times in self.data.items():
            if date[5:] == today_str:  # ignore year
                day = times
                break

        if day:
            for prayer, time_label in self.prayer_columns:
                time_label.configure(text=day.get(prayer,"--:--"))
        else:
            for _, time_label in self.prayer_columns:
                time_label.configure(text="--:--")

        self.update_next_prayer()

    def tick(self):
        self.update_display()
        self.root.after(REFRESH_INTERVAL_MS, self.tick)

# --------------------------
if __name__=="__main__":
    root = ctk.CTk()
    app = MosqueApp(root)
    root.mainloop()