# mosque_app.py
import customtkinter as ctk
from PIL import Image, ImageTk
import datetime
import sys
import os

if sys.stdout is not None:
    sys.stdout.reconfigure(encoding='utf-8')

# استيراد الموديولات
from config import *
from utils import *
from audio_manager import AudioManager
from overlay_manager import OverlayManager
from prayer_times import PrayerTimes
from theme_manager import ThemeManager

class MosqueApp:
    def __init__(self, root):
        self.root = root
        self.root.title(MOSQUE_NAME)
        
        # تهيئة الموديولات
        self.theme_manager = ThemeManager()
        self.audio_manager = AudioManager()
        
        # إنشاء الأيقونة
        create_mosque_icon()
        self._setup_icon()
        
        # إعداد الشاشة
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda e: self.toggle_fullscreen())
        self.root.bind("<F1>", lambda e: self.test_adhan_maghrib())
        
        # تحميل البيانات
        csv_data, self.place = load_csv()
        self.prayer_times = PrayerTimes(csv_data)
        
        # إعداد الواجهة
        self._setup_ui()
        
        # تهيئة الـ overlay
        self.overlay_manager = OverlayManager(self.root, self.font_scales, self.audio_manager)
        
        # بدء التحديث
        self.last_adhan_played = None
        self.update_display()
        self.root.after(REFRESH_INTERVAL_MS, self.tick)
    
    def _setup_icon(self):
        """إعداد أيقونة التطبيق"""
        try:
            icon_paths = [
                "mosque.ico",
                resource_path("mosque.ico"),
                "icon.ico", 
                resource_path("icon.ico"),
                os.path.join(os.path.dirname(__file__), "mosque.ico")
            ]
            
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
                    print(f"تم تعيين الأيقونة: {icon_path}")
                    return
            
            print("تحذير: لم يتم العثور على أيقونة التطبيق")
        except Exception as e:
            print(f"خطأ في تحميل الأيقونة: {e}")
    
    def _setup_ui(self):
        """إعداد واجهة المستخدم"""
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        
        print(f"دقة الشاشة: {screen_w} x {screen_h}")
        self.font_scales = calculate_font_scales(screen_w, screen_h)
        print(f"عامل التحجيم: {self.font_scales['scale_factor']:.1f}")

        # الخلفية
        self._setup_background()
        
        # الحاوية الرئيسية
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True)

        # الأزرار العلوية
        self._setup_top_buttons(main_container)
        
        # العناوين
        self._setup_titles(main_container)
        
        # قسم الصلاة القادمة
        self._setup_next_prayer_section(main_container)
        
        # جدول أوقات الصلاة
        self._setup_prayer_schedule(main_container)
    
    def _setup_background(self):
        """إعداد خلفية التطبيق"""
        bg_file = resource_path(BACKGROUND_FILE)
        colors = self.theme_manager.get_colors()
        
        if os.path.exists(bg_file):
            try:
                bg_img = Image.open(bg_file)
                self.bg_image = ctk.CTkImage(
                    light_image=bg_img,
                    dark_image=bg_img,
                    size=(self.root.winfo_screenwidth(), self.root.winfo_screenheight())
                )
                self.bg_label = ctk.CTkLabel(self.root, image=self.bg_image, text="")
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            except Exception as e:
                print(f"Error loading background: {e}")
                self._create_solid_background(colors["bg_color"])
        else:
            print(f"Background file not found: {bg_file}")
            self._create_solid_background(colors["bg_color"])
    
    def _create_solid_background(self, color):
        """إنشاء خلفية صلبة"""
        self.bg_label = ctk.CTkLabel(self.root, text="", fg_color=color)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    def _setup_top_buttons(self, parent):
        """إعداد الأزرار العلوية"""
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent", height=self.font_scales['button_height'])
        btn_frame.pack(side="top", fill="x", padx=20, pady=10)
        btn_frame.pack_propagate(False)

        button_container = ctk.CTkFrame(btn_frame, fg_color="transparent")
        button_container.pack(side="right")

        # زر الإغلاق
        close_btn = self._create_button(button_container, CLOSE_IMG, "X", "#E74C3C", self.root.destroy)
        close_btn.pack(side="right", padx=5)

        # زر التصغير
        min_btn = self._create_button(button_container, MINIMIZE_IMG, "_", "#3498DB", self.root.iconify)
        min_btn.pack(side="right", padx=5)
    
    def _create_button(self, parent, img_path, text, color, command):
        """إنشاء زر"""
        img_path = resource_path(img_path)
        if os.path.exists(img_path):
            try:
                img = Image.open(img_path)
                icon = ctk.CTkImage(light_image=img, dark_image=img, size=(20, 20))
                return ctk.CTkButton(
                    parent, image=icon, text="", width=30, height=30,
                    fg_color=color, hover_color=color, command=command
                )
            except Exception as e:
                print(f"Error loading icon {img_path}: {e}")
        
        return ctk.CTkButton(
            parent, text=text, width=30, height=30,
            fg_color=color, hover_color=color, font=("Arial", 16, "bold"), command=command
        )
    
    def _setup_titles(self, parent):
        """إعداد العناوين"""
        colors = self.theme_manager.get_colors()
        
        # اسم المسجد
        self.mosque_label = ctk.CTkLabel(
            parent, text=MOSQUE_NAME,
            font=("Arial", self.font_scales['mosque_font'], "bold"),
            text_color=colors["title"], fg_color="transparent"
        )
        self.mosque_label.pack(pady=(self.font_scales['title_pady'], 5))

        # المكان
        self.place_label = ctk.CTkLabel(
            parent, text=PLACE_NAME,
            font=("Arial", self.font_scales['place_font']),
            text_color=colors["text_color"], fg_color="transparent"
        )
        self.place_label.pack(pady=(10, 2))

        # التاريخ والوقت
        self.date_label = ctk.CTkLabel(
            parent, text="",
            font=("Arial", self.font_scales['date_font']),
            text_color=colors["text_color"], fg_color="transparent"
        )
        self.date_label.pack(pady=(0, 5))
    
    def _setup_next_prayer_section(self, parent):
        """إعداد قسم الصلاة القادمة"""
        colors = self.theme_manager.get_colors()
        
        next_prayer_frame = ctk.CTkFrame(
            parent, width=self.font_scales['next_prayer_width'],
            height=self.font_scales['next_prayer_height'],
            fg_color=colors["prayer_bg"], corner_radius=20,
            border_width=2, border_color=colors["prayer_border"]
        )
        next_prayer_frame.pack(pady=self.font_scales['center_pady'], expand=True)
        next_prayer_frame.pack_propagate(False)

        next_prayer_container = ctk.CTkFrame(next_prayer_frame, fg_color="transparent")
        next_prayer_container.pack(expand=True, fill="both")

        # عنوان القسم
        self.next_title = ctk.CTkLabel(
            next_prayer_container, text="الصلاة القادمة",
            font=("Arial", self.font_scales['next_title_font'], "bold"),
            text_color=colors["text_color"]
        )
        self.next_title.pack(pady=(20, 5))

        # اسم الصلاة
        self.next_name = ctk.CTkLabel(
            next_prayer_container, text="",
            font=("Arial", self.font_scales['next_name_font'], "bold"),
            text_color="gold"
        )
        self.next_name.pack(pady=10)

        # العد التنازلي
        self.countdown = ctk.CTkLabel(
            next_prayer_container, text="",
            font=("Arial", self.font_scales['countdown_font']),
            text_color=colors["countdown_color"]
        )
        self.countdown.pack(pady=(5, 15))
    
    def _setup_prayer_schedule(self, parent):
        """إعداد جدول أوقات الصلاة"""
        colors = self.theme_manager.get_colors()
        
        schedule_frame = ctk.CTkFrame(
            parent, fg_color=colors["schedule_bg"],
            corner_radius=25, height=self.font_scales['schedule_height']
        )
        schedule_frame.pack(side="bottom", pady=self.font_scales['bottom_pady'], padx=50, fill="x")
        schedule_frame.pack_propagate(False)

        # عنوان الجدول
        schedule_title = ctk.CTkLabel(
            schedule_frame, text="أوقات الصلاة اليوم",
            font=("Arial", self.font_scales['schedule_title_font'], "bold"),
            text_color=colors["text_color"]
        )
        schedule_title.pack(pady=15)

        # الأعمدة
        self._setup_prayer_columns(schedule_frame)
    
    def _setup_prayer_columns(self, parent):
        """إعداد أعمدة أوقات الصلاة"""
        colors = self.theme_manager.get_colors()
        columns_container = ctk.CTkFrame(parent, fg_color="transparent")
        columns_container.pack(pady=10)

        self.prayer_columns = []
        prayers = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]

        for i, prayer in enumerate(prayers):
            reverse_i = len(prayers) - 1 - i
            
            column_frame = ctk.CTkFrame(
                columns_container, width=self.font_scales['column_width'],
                height=self.font_scales['column_height'], fg_color=colors["column_bg"],
                corner_radius=15, border_width=2, border_color=colors["prayer_border"]
            )
            column_frame.grid(row=0, column=reverse_i, padx=self.font_scales['column_padx'], pady=5)
            column_frame.grid_propagate(False)
            column_frame.pack_propagate(False)
            
            # اسم الصلاة
            name_label = ctk.CTkLabel(
                column_frame, text=DISPLAY_NAMES[prayer],
                font=("Arial", self.font_scales['prayer_name_font'], "bold"),
                text_color="#FFD700"
            )
            name_label.pack(pady=(15, 5))
            
            # وقت الصلاة
            time_label = ctk.CTkLabel(
                column_frame, text="--:--",
                font=("Arial", self.font_scales['prayer_time_font'], "bold"),
                text_color=colors["countdown_color"]
            )
            time_label.pack(pady=(5, 15))
            
            self.prayer_columns.append((prayer, time_label))
    
    def toggle_fullscreen(self):
        """تبديل وضع ملء الشاشة"""
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))
    
    def test_adhan_maghrib(self):
        """اختبار الأذان للمغرب"""
        self.overlay_manager.show_adhan_overlay("Maghrib")
    
    def update_display(self):
        """تحديث العرض"""
        now = datetime.datetime.now()
        weekday_ar = ["الاثنين","الثلاثاء","الأربعاء","الخميس","الجمعة","السبت","الأحد"]
        self.date_label.configure(
            text=f"{weekday_ar[now.weekday()]}، {now.day} / {now.month} / {now.year} - {now.strftime('%H:%M:%S')}"
        )
        
        # تحديث الثيم
        self.theme_manager.update_theme()
        
        # تحديث أوقات الصلاة
        today_times = self.prayer_times.get_today_times()
        if today_times:
            for prayer, time_label in self.prayer_columns:
                time_label.configure(text=today_times.get(prayer, "--:--"))
        else:
            for _, time_label in self.prayer_columns:
                time_label.configure(text="--:--")

        # تحديث الصلاة القادمة
        self.update_next_prayer()
    
    def update_next_prayer(self):
        """تحديث الصلاة القادمة"""
        key, dt = self.prayer_times.find_next_prayer()
        if key and dt:
            self.next_name.configure(text=self.prayer_times.get_prayer_display_name(key))
            remaining = dt - datetime.datetime.now()
            total = int(remaining.total_seconds())
            if total < 0: total = 0
            
            h = total // 3600
            m = (total % 3600) // 60
            s = total % 60
            
            if h > 0:
                self.countdown.configure(text=f"باقي : {h:02d}:{m:02d}:{s:02d}")
            else:
                self.countdown.configure(text=f"باقي : {m:02d}:{s:02d}")

            if total <= 1 and self.last_adhan_played != key:
                self.last_adhan_played = key
                self.overlay_manager.show_adhan_overlay(key)
        else:
            self.next_name.configure(text="--")
            self.countdown.configure(text="")
    
    def tick(self):
        """دورة التحديث"""
        self.update_display()
        self.root.after(REFRESH_INTERVAL_MS, self.tick)

# التشغيل الرئيسي
if __name__ == "__main__":
    root = ctk.CTk()
    app = MosqueApp(root)
    root.mainloop()