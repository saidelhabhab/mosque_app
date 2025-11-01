# mosque_app.csv
import customtkinter as ctk
from PIL import Image, ImageTk
import datetime
import sys
import os
import time
import random

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
        # create_mosque_icon()
        self._setup_icon()
        
        # إعداد الشاشة
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda e: self.toggle_fullscreen())
        self.root.bind("<F1>", lambda e: self.test_adhan_maghrib())
        
        # تحميل البيانات
        csv_data, self.place = load_csv()
        self.prayer_times = PrayerTimes(csv_data)
        
        # ⭐⭐ إضافة هذا السطر: تعريف is_jumaa قبل استخدامه ⭐⭐
        self.is_jumaa = False  # القيمة الافتراضية
        
        # إعداد الواجهة
        self._setup_ui()
        
        # تهيئة الـ overlay
        self.overlay_manager = OverlayManager(self.root, self.font_scales, self.audio_manager)
        
        # تهيئة نظام الأذكار
        self._setup_azkar_system()
        
        # تهيئة نظام الجمعة الخاص
        self._setup_jumaa_system()
        
        # بدء التحديث
        self.last_adhan_played = None
        self.last_prayer_completed = None
        self.update_display()
        self._check_jumaa_day()  # ✅ الآن ستعمل بدون خطأ
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
    
    def _check_jumaa_day(self):
        """التحقق كل ساعة مما إذا كان اليوم جمعة"""
        now = datetime.datetime.now()
        weekday = now.weekday()  # 0 = Monday ... 4 = Friday
        
        if weekday == 4:
            # اليوم جمعة
            print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] 🕌 اليوم جمعة - سيتم استخدام صلاة الجمعة (بدل الظهر)")
            self.is_jumaa = True
        else:
            # باقي الأيام - إعادة تعيين العلامات
            if self.is_jumaa:  # إذا كان اليوم جمعة وأصبح غير جمعة
                self._reset_jumaa_flags()
            self.is_jumaa = False
            print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] 📅 اليوم عادي (ليس جمعة)")
        
        # إعادة التحقق كل ساعة (3600000 ms)
        self.root.after(3600000, self._check_jumaa_day)

    def _setup_ui(self):
        """إعداد واجهة المستخدم"""
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        
        print(f"دقة الشاشة: {screen_w} x {screen_h}")
        self.font_scales = calculate_font_scales(screen_w, screen_h)
        print(f"عامل التحجيم: {self.font_scales['scale_factor']:.1f}")

        # الخلفية - يجب أن تكون أول شيء
        self.root.after(500, self._setup_background)
    
        # الحاوية الرئيسية
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True)

        # الأزرار العلوية
        self._setup_top_buttons(main_container)
        
        # العناوين
        self._setup_titles(main_container)
        
        # قسم الصلاة القادمة
        self._setup_next_prayer_section(main_container)
        
        # قسم المعلومات الإضافية (الشروق والجمعة)
        self._setup_additional_info(main_container)
        
        # جدول أوقات الصلاة
        self._setup_prayer_schedule(main_container)
    
    def _setup_background(self):
        """إعداد خلفية التطبيق باستخدام CTkImage بشكل صحيح"""
        # البحث عن ملف الخلفية في مسارات مختلفة
        possible_paths = [
            "background.jpg",
            r"C:\Users\saidt\Desktop\mosque_app-master\background.jpg",
            os.path.join(os.path.dirname(__file__), "background.jpg"),
            resource_path("background.jpg"),
            BACKGROUND_FILE
        ]
        
        bg_file_found = None
        for path in possible_paths:
            if os.path.exists(path):
                bg_file_found = path
                print(f"تم العثور على خلفية: {path}")
                break
        
        if bg_file_found:
            try:
                # تحميل الصورة باستخدام PIL
                print(f"جاري تحميل الخلفية من: {bg_file_found}")
                bg_img = Image.open(bg_file_found)
                
                # تحجيم الصورة لتناسب الشاشة
                screen_w = self.root.winfo_screenwidth()
                screen_h = self.root.winfo_screenheight()
                print(f"تحجيم الصورة إلى: {screen_w} x {screen_h}")
                
                bg_img_resized = bg_img.resize((screen_w, screen_h), Image.Resampling.LANCZOS)
                
                # استخدام CTkImage بشكل صحيح
                self.bg_ctk_image = ctk.CTkImage(
                    light_image=bg_img_resized,
                    dark_image=bg_img_resized,
                    size=(screen_w, screen_h)
                )
                
                # استخدام CTkLabel مع CTkImage - بدون لون خلفية
                self.bg_label = ctk.CTkLabel(
                    self.root, 
                    image=self.bg_ctk_image, 
                    text=""
                )
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                
                # تأكد من أن الخلفية في الخلف
                self.bg_label.lower()
                
                print("تم تحميل الخلفية بنجاح باستخدام CTkImage")
                
            except Exception as e:
                print(f"خطأ في تحميل الخلفية: {e}")
                print("استخدام خلفية صلبة بدلاً من الصورة")
                self._create_solid_background("#1a1a1a")
        else:
            print("لم يتم العثور على ملف الخلفية في المسارات التالية:")
            for path in possible_paths:
                print(f"  - {path}")
            print("استخدام لون خلفية افتراضي")
            self._create_solid_background("#1a1a1a")

    def _create_solid_background(self, color):
        """إنشاء خلفية صلبة"""
        print(f"إنشاء خلفية صلبة باللون: {color}")
        self.bg_label = ctk.CTkLabel(
            self.root, 
            text="", 
            fg_color=color
        )
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.lower()
    
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
                    parent, image=icon, text="", width=30, height=2,
                    fg_color=color, hover_color=color, command=command
                )
            except Exception as e:
                print(f"Error loading icon {img_path}: {e}")
        
        return ctk.CTkButton(
            parent, text=text, width=30, height=2,
            fg_color=color, hover_color=color, font=("Arial", 14, "bold"), command=command
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
        self.mosque_label.pack(pady=(self.font_scales['title_pady'], 0))

        # المكان
        self.place_label = ctk.CTkLabel(
            parent, text=PLACE_NAME,
            font=("Arial", self.font_scales['place_font']),
            text_color=colors["text_color"], fg_color="transparent"
        )
        self.place_label.pack(pady=(3, 0))

        # التاريخ والوقت
        self.date_label = ctk.CTkLabel(
            parent, text="",
            font=("Arial", self.font_scales['date_font']),
            text_color=colors["text_color"], fg_color="transparent"
        )
        self.date_label.pack(pady=(0, 2))
    
    def _setup_next_prayer_section(self, parent):
        """إعداد قسم الصلاة القادمة"""
        colors = self.theme_manager.get_colors()
        
        next_prayer_frame = ctk.CTkFrame(
            parent, width=self.font_scales['next_prayer_width'],
            height=self.font_scales['next_prayer_height'],
            fg_color=colors["prayer_bg"],
            corner_radius=25,  # ⬅️ غير هذه القيمة إلى ما تريد (مثلاً: 25)
            border_width=2, 
            border_color=colors["prayer_border"]
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
        self.next_title.pack(pady=(3, 0))

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

        self.countdown.pack(pady=(0, 0))
    
    def _setup_additional_info(self, parent):
        """إعداد قسم المعلومات الإضافية (الشروق والجمعة)"""
        colors = self.theme_manager.get_colors()
        
        # إطار المعلومات الإضافية
        info_frame = ctk.CTkFrame(
            parent, 
            fg_color=colors["schedule_bg"],
            corner_radius=15,
            height=88
        )
        info_frame.pack(pady=5, padx=40, fill="x")
        info_frame.pack_propagate(False)
        
        info_container = ctk.CTkFrame(info_frame, fg_color="transparent")
        info_container.pack(expand=True, fill="both", padx=20, pady=10)
        
        # قسم الشروق
        sunrise_frame = ctk.CTkFrame(info_container, fg_color="transparent")
        sunrise_frame.pack(side="left", padx=15)
        
        sunrise_title = ctk.CTkLabel(
            sunrise_frame,
            text="🌅 وقت الشروق",
            font=("Arial", self.font_scales['prayer_name_font'], "bold"),
            text_color="#FFD700"
        )
        sunrise_title.pack()
        
        self.sunrise_time = ctk.CTkLabel(
            sunrise_frame,
            text="--:--",
            font=("Arial", self.font_scales['prayer_time_font'], "bold"),
            text_color=colors["countdown_color"]
        )
        self.sunrise_time.pack()
        
        # قسم صلاة الجمعة
        jumaa_frame = ctk.CTkFrame(info_container, fg_color="transparent")
        jumaa_frame.pack(side="right", padx=15)
        
        jumaa_title = ctk.CTkLabel(
            jumaa_frame,
            text="🕌 صلاة الجمعة",
            font=("Arial", self.font_scales['prayer_name_font'], "bold"),
            text_color="#FFD700"
        )
        jumaa_title.pack()
        
        self.jumaa_time = ctk.CTkLabel(
            jumaa_frame,
            text="12:30",  # وقت افتراضي لصلاة الجمعة
            font=("Arial", self.font_scales['prayer_time_font'], "bold"),
            text_color=colors["countdown_color"]
        )
        self.jumaa_time.pack()
    
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
        schedule_title.pack(pady=10)

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
    
    def _setup_jumaa_system(self):
        """إعداد نظام الجمعة الخاص"""
        # حالات نظام الجمعة
        self.jumaa_dark_page_visible = False
        self.jumaa_prayer_page_visible = False
        self.jumaa_adhan_played = False
        self.jumaa_iqama_played = False
        self.azkar_started = False  # إضافة هذا المتغير
        
        # إنشاء صفحة الخطبة (سوداء)
        self._create_khotba_page()
        
        # إنشاء صفحة الصلاة (بدون عداد)
        self._create_jumaa_prayer_page()

    def _reset_jumaa_flags(self):
        """إعادة تعيين علامات الجمعة"""
        self.jumaa_dark_page_visible = False
        self.jumaa_prayer_page_visible = False
        self.jumaa_adhan_played = False
        self.jumaa_iqama_played = False
        self.azkar_started = False
        print("🔄 إعادة تعيين علامات نظام الجمعة")
    
    def _create_khotba_page(self):
        """إنشاء صفحة الخطبة السوداء"""
        self.khotba_frame = ctk.CTkFrame(
            self.root,
            fg_color="#000000",  # خلفية سوداء بالكامل
            corner_radius=0
        )
        self.khotba_frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        # نص الخطبة في المنتصف
        self.khotba_label = ctk.CTkLabel(
            self.khotba_frame,
            text="🕌 خطبة الجمعة\n\nيرجى الإنصات للخطيب",
            font=("Arial", 80, "bold"),
            text_color="#FFFFFF",
            justify="center"
        )
        self.khotba_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # عداد الوقت المتبقي للخطبة
        self.khotba_timer = ctk.CTkLabel(
            self.khotba_frame,
            text="⏳ وقت الخطبة: 15:00",
            font=("Arial", 40, "bold"),
            text_color="#FFD700"
        )
        self.khotba_timer.place(relx=0.5, rely=0.8, anchor="center")
        
        # إخفاء الصفحة في البداية
        self.khotba_frame.place_forget()
    
    def _create_jumaa_prayer_page(self):
        """إنشاء صفحة الصلاة بدون عداد"""
        self.jumaa_prayer_frame = ctk.CTkFrame(
            self.root,
            fg_color="#0A1F3A",
            corner_radius=0
        )
        self.jumaa_prayer_frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        # محتوى صفحة الصلاة
        center_frame = ctk.CTkFrame(self.jumaa_prayer_frame, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # أيقونة المسجد
        self.jumaa_icon = ctk.CTkLabel(
            center_frame,
            text="🕌",
            font=("Arial", 120, "bold"),
            text_color="gold"
        )
        self.jumaa_icon.pack(pady=(0, 30))
        
        # نص الصلاة
        self.jumaa_prayer_label = ctk.CTkLabel(
            center_frame,
            text="صلاة الجمعة",
            font=("Arial", 80, "bold"),
            text_color="#FFFFFF"
        )
        self.jumaa_prayer_label.pack(pady=(0, 20))
        
        # نص توجيهي
        self.jumaa_instruction = ctk.CTkLabel(
            center_frame,
            text="الرجاء متابعة الإمام في الصلاة",
            font=("Arial", 40),
            text_color="#87CEEB"
        )
        self.jumaa_instruction.pack(pady=(0, 10))
        
        # مؤقت الصلاة
        self.jumaa_prayer_timer = ctk.CTkLabel(
            center_frame,
            text="⏳ 00:30",
            font=("Arial", 50, "bold"),
            text_color="#FFD700"
        )
        self.jumaa_prayer_timer.pack(pady=(20, 0))
        
        # إخفاء الصفحة في البداية
        self.jumaa_prayer_frame.place_forget()
    
    def _start_jumaa_khotba(self):
        """بدء فترة الخطبة (15 دقيقة)"""
        if self.jumaa_dark_page_visible:
            return
            
        print("🕌 بدء فترة الخطبة - 15 دقيقة")
        self.jumaa_dark_page_visible = True
        
        # إظهار صفحة الخطبة السوداء
        self.khotba_frame.lift()
        self.khotba_frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        # بدء العد التنازلي للخطبة (15 دقيقة)
        self.khotba_remaining = 15 * 60  # 15 دقيقة بالثواني
        self._update_khotba_timer()
    
    def _update_khotba_timer(self):
        """تحديث عداد الخطبة"""
        if not self.jumaa_dark_page_visible:
            return
            
        self.khotba_remaining -= 1
        
        if self.khotba_remaining <= 0:
            # انتهت فترة الخطبة، الانتقال للإقامة
            self._end_khotba_period()
            return
        
        # تحديث العداد
        minutes = self.khotba_remaining // 60
        seconds = self.khotba_remaining % 60
        self.khotba_timer.configure(text=f"⏳ وقت الخطبة: {minutes:02d}:{seconds:02d}")
        
        # الاستمرار في العد
        self.root.after(1000, self._update_khotba_timer)
    
    def _end_khotba_period(self):
        """إنهاء فترة الخطبة وبدء الإقامة"""
        print("🕌 انتهت فترة الخطبة، بدء الإقامة مباشرة")
        self.jumaa_dark_page_visible = False
        self.khotba_frame.place_forget()
        
        # تشغيل الإقامة مباشرة (بدون عد تنازلي)
        self.overlay_manager.play_iqama_directly("Dhuhr")
        
        # بعد 30 ثانية من الإقامة، عرض صفحة الصلاة
        # self.root.after(30000, self._show_jumaa_prayer_page)  # 30 ثانية
    
    def _show_jumaa_prayer_page(self):
        """عرض صفحة الصلاة بعد الإقامة"""
        if self.jumaa_prayer_page_visible:
            return  # منع التكرار إذا الصفحة معروضة بالفعل
            
        print("🕌 عرض صفحة الصلاة بعد الإقامة بـ 30 ثانية")
        self.jumaa_prayer_page_visible = True
        
        # إظهار صفحة الصلاة
        self.jumaa_prayer_frame.lift()
        self.jumaa_prayer_frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        # بدء العد التنازلي للصلاة (30 ثانية)
        self.prayer_remaining = 30  # 30 ثانية
        self._update_prayer_timer()
    
    def _update_prayer_timer(self):
        """تحديث عداد الصلاة"""
        if not self.jumaa_prayer_page_visible:
            return
            
        self.prayer_remaining -= 1
        
        if self.prayer_remaining <= 0:
            # انتهت فترة الصلاة، الانتقال للأذكار
            self._end_prayer_period()
            return
        
        # تحديث العداد
        self.jumaa_prayer_timer.configure(text=f"⏳ {self.prayer_remaining:02d}")
        
        # الاستمرار في العد
        self.root.after(1000, self._update_prayer_timer)
    
    def _end_prayer_period(self):
        """إنهاء فترة الصلاة وبدء الأذكار"""
        print("🕌 انتهت فترة الصلاة، بدء الأذكار بعد 5 دقائق")
        self.jumaa_prayer_page_visible = False
        self.jumaa_prayer_frame.place_forget()
        
        # بعد 5 دقائق من الإقامة، عرض الأذكار
        self.root.after(5 * 60 * 1000, self._start_jumaa_azkar)  # 5 دقائق
    
    def _start_jumaa_azkar(self):
        """بدء الأذكار بعد صلاة الجمعة"""
        if getattr(self, 'azkar_started', False):
            print("⛔ الأذكار بدأت بالفعل - منع التكرار")
            return  # منع التكرار إذا الأذكار بدأت بالفعل
            
        print("🕌 بدء الأذكار بعد صلاة الجمعة")
        self.azkar_started = True
        
        # تعيين أن صلاة الظهر قد اكتملت (لمنع النظام العادي من عرض الأذكار)
        self.last_prayer_completed = "Dhuhr"
        
        # عرض الأذكار
        self.show_zekr("Dhuhr")
    
    def _check_jumaa_schedule(self):
        """التحقق من جدول الجمعة مع التوقيتات الجديدة"""
        now = datetime.datetime.now()
        
        # التحقق إذا كان اليوم جمعة
        if now.weekday() != 4:  # 4 = الجمعة
            return False
    
        # الحصول على وقت صلاة الجمعة (الظهر)
        jumaa_time = self._get_prayer_time_today("Dhuhr")
        if not jumaa_time:
            return False
        
        # الوقت الحالي
        current_time = now
        
        # 1 دقيقة بعد الأذان - بدء الخطبة
        khotba_start_time = jumaa_time + datetime.timedelta(minutes=1)
        if khotba_start_time <= current_time <= khotba_start_time + datetime.timedelta(seconds=10):
            if not self.jumaa_adhan_played:
                print("🕌 وقت الجمعة - بدء الخطبة بعد الأذان بـ 1 دقيقة")
                self.jumaa_adhan_played = True
                self._start_jumaa_khotba()
                return True
        
        # بعد الإقامة بـ 30 ثانية - عرض صفحة الصلاة
        iqama_time = jumaa_time + datetime.timedelta(minutes=1 + 15)  # 1 دقيقة أذان + 15 دقيقة خطبة
        if iqama_time <= current_time <= iqama_time + datetime.timedelta(seconds=40):
            if not self.jumaa_iqama_played and not self.jumaa_prayer_page_visible:
                print("🕌 وقت الإقامة - عرض صفحة الصلاة بعد 30 ثانية")
                self.jumaa_iqama_played = True
                # إيقاف أي overlay للإقامة
                self.overlay_manager.stop_iqama_countdown()
                # عرض صفحة الصلاة مباشرة
                self._show_jumaa_prayer_page()
                return True
        
        return False
    
    def toggle_fullscreen(self):
        """تبديل وضع ملء الشاشة"""
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))
    
    def test_adhan_maghrib(self):
        """اختبار الأذان للمغرب"""
        self.overlay_manager.show_adhan_overlay("Maghrib")
    
    def _setup_azkar_system(self):
        """إعداد نظام الأذكار بعد الصلوات"""
        self.azkar_times = {
            "Fajr": 25 * 60,     
            "Dhuhr": 22 * 60,
            "Asr": 22 * 60,
            "Maghrib": 16 * 60,
            "Isha": 22 * 60
        }
                
        # أذكار خاصة لكل صلاة (10 تسبيحات) - صفحة الأذكار
        self.azkar_by_prayer = {
            "Fajr": [
                "أستغفر الله، أستغفر الله، أستغفر الله، اللهم أنت السلام ومنك السلام تباركت يا ذا الجلال والإكرام",
                "(33) سبحان الله (33) الحمد لله (33) الله أكبر ",
                "لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير",
                "آية الكرسي\n"
                "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ ۚ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ\n"
                "لَهُ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ ۗ مَن ذَا الَّذِي يَشْفَعُ عِندَهُ إِلَّا بِإِذْنِهِ\n"
                "يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ وَلَا يُحِيطُونَ بِشَيْءٍ مِّنْ عِلْمِهِ إِلَّا بِمَا شَاءَ\n"
                "وَسِعَ كُرْسِيُّهُ السَّمَاوَاتِ وَالْأَرْضَ وَلَا يَئُودُهُ حِفْظُهُمَا ۚ وَهُوَ الْعَلِيُّ الْعَظِيمُ"
            ],
            "Dhuhr": [
                "أستغفر الله، أستغفر الله، أستغفر الله، اللهم أنت السلام ومنك السلام تباركت يا ذا الجلال والإكرام",
                "سبحان الله (33) الحمد لله (33) الله أكبر (33)",
                "لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير",
                "آية الكرسي\n"
                "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ ۚ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ\n"
                "لَهُ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ ۗ مَن ذَا الَّذِي يَشْفَعُ عِندَهُ إِلَّا بِإِذْنِهِ\n"
                "يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ وَلَا يُحِيطُونَ بِشَيْءٍ مِّنْ عِلْمِهِ إِلَّا بِمَا شَاءَ\n"
                "وَسِعَ كُرْسِيُّهُ السَّمَاوَاتِ وَالْأَرْضَ وَلَا يَئُودُهُ حِفْظُهُمَا ۚ وَهُوَ الْعَلِيُّ الْعَظِيمُ"
            ],
            "Asr": [
                "أستغفر الله، أستغفر الله، أستغفر الله، اللهم أنت السلام ومنك السلام تباركت يا ذا الجلال والإكرام",
                "سبحان الله (33) الحمد لله (33) الله أكبر (33)",
                "لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير",
                "آية الكرسي\n"
                "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ ۚ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ\n"
                "لَهُ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ ۗ مَن ذَا الَّذِي يَشْفَعُ عِندَهُ إِلَّا بِإِذْنِهِ\n"
                "يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ وَلَا يُحِيطُونَ بِشَيْءٍ مِّنْ عِلْمِهِ إِلَّا بِمَا شَاءَ\n"
                "وَسِعَ كُرْسِيُّهُ السَّمَاوَاتِ وَالْأَرْضَ وَلَا يَئُودُهُ حِفْظُهُمَا ۚ وَهُوَ الْعَلِيُّ الْعَظِيمُ"
            ],
            "Maghrib": [
                "أستغفر الله، أستغفر الله، أستغفر الله، اللهم أنت السلام ومنك السلام تباركت يا ذا الجلال والإكرام",
                "سبحان الله (33) الحمد لله (33) الله أكبر (33)",
                "لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير",
                "آية الكرسي\n"
                "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ ۚ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ\n"
                "لَهُ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ ۗ مَن ذَا الَّذِي يَشْفَعُ عِندَهُ إِلَّا بِإِذْنِهِ\n"
                "يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ وَلَا يُحِيطُونَ بِشَيْءٍ مِّنْ عِلْمِهِ إِلَّا بِمَا شَاءَ\n"
                "وَسِعَ كُرْسِيُّهُ السَّمَاوَاتِ وَالْأَرْضَ وَلَا يَئُودُهُ حِفْظُهُمَا ۚ وَهُوَ الْعَلِيُّ الْعَظِيمُ"
            ],
            "Isha": [
                "أستغفر الله، أستغفر الله، أستغفر الله، اللهم أنت السلام ومنك السلام تباركت يا ذا الجلال والإكرام",
                "سبحان الله (33) الحمد لله (33) الله أكبر (33)",
                "لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير",
                "آية الكرسي\n"
                "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ ۚ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ\n"
                "لَهُ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ ۗ مَن ذَا الَّذِي يَشْفَعُ عِندَهُ إِلَّا بِإِذْنِهِ\n"
                "يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ وَلَا يُحِيطُونَ بِشَيْءٍ مِّنْ عِلْمِهِ إِلَّا بِمَا شَاءَ\n"
                "وَسِعَ كُرْسِيُّهُ السَّمَاوَاتِ وَالْأَرْضَ وَلَا يَئُودُهُ حِفْظُهُمَا ۚ وَهُوَ الْعَلِيُّ الْعَظِيمُ"
            ]
        }

        # سور الإخلاص والمعوذتين - صفحة السور
        self.surahs = [
            {
                "title": "سورة الإخلاص",
                "text": (
                    "① قُلْ هُوَ اللَّهُ أَحَدٌ \n"
                    "② اللَّهُ الصَّمَدُ \n"
                    "③ لَمْ يَلِدْ وَلَمْ يُولَدْ \n"
                    "④ وَلَمْ يَكُن لَّهُ كُفُوًا أَحَدٌ "
                )
            },
            {
                "title": "سورة الفلق",
                "text": (
                    "① قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ \n"
                    "② مِن شَرِّ مَا خَلَقَ \n"
                    "③ وَمِن شَرِّ غَاسِقٍ إِذَا وَقَبَ \n"
                    "④ وَمِن شَرِّ النَّفَّاثَاتِ فِي الْعُقَدِ \n"
                    "⑤ وَمِن شَرِّ حَاسِدٍ إِذَا حَسَدَ \n"
                    "اللهم اجعلنا من المحصنين بها من كل شرٍّ وسوءٍ."
                )
            },
            {
                "title": "سورة الناس",
                "text": (
                    "① قُلْ أَعُوذُ بِرَبِّ النَّاسِ \n"
                    "② مَلِكِ النَّاسِ \n"
                    "③ إِلَٰهِ النَّاسِ \n"
                    "④ مِن شَرِّ الْوَسْوَاسِ الْخَنَّاسِ \n"
                    "⑤ الَّذِي يُوَسْوِسُ فِي صُدُورِ النَّاسِ \n"
                    "⑥ مِنَ الْجِنَّةِ وَالنَّاسِ "
                )
            }
        ]

        # باقي الإعدادات
        self.current_zekr_index = 0
        self.current_surah_index = 0
        self.zekr_visible = False
        self.surah_visible = False
        self.zekr_start_time = None
        self.surah_start_time = None
        self.current_prayer_for_azkar = None

        # إنشاء عناصر الأذكار والسور
        self._create_zekr_widget()
        self._create_surah_widget()
    
    def _create_zekr_widget(self):
        """إنشاء عنصر عرض الأذكار (صفحة كاملة)"""
        # إنشاء إطار كامل الشاشة للأذكار
        self.zekr_frame = ctk.CTkFrame(
            self.root,
            fg_color="#0A1F3A",
            corner_radius=0
        )
        self.zekr_frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        # حاوية مركزية للأذكار
        center_frame = ctk.CTkFrame(
            self.zekr_frame,
            fg_color="transparent"
        )
        center_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.8)
        
        # أيقونة المسجد
        self.zekr_icon = ctk.CTkLabel(
            center_frame,
            text="🕌",
            font=("Arial", 110, "bold"),
            text_color="gold"
        )
        self.zekr_icon.pack(pady=(20, 10))
        
        # عنوان الصلاة
        self.zekr_prayer_title = ctk.CTkLabel(
            center_frame,
            text="",
            font=("Arial", 50, "bold"),
            text_color="#FFD700"
        )
        self.zekr_prayer_title.pack(pady=(0, 20))
    
        
        # نص الذكر الخاص بالصلاة
        self.zekr_label = ctk.CTkLabel(
            center_frame,
            text="",
            font=("Arial", 70),
            text_color="#FFFFFF",
            wraplength=1100,
            justify="center"
        )
        self.zekr_label.pack(pady=20, padx=50, fill="both", expand=True)
        
        # تذييل مع رقم الذكر الحالي
        self.zekr_footer = ctk.CTkLabel(
            center_frame,
            text="",
            font=("Arial", 18),
            text_color="#87CEEB"
        )
        self.zekr_footer.pack(pady=4)
        
        # زر العودة (خفيف في الزاوية)
        self.zekr_back_button = ctk.CTkButton(
            self.zekr_frame,
            text="العودة",
            font=("Arial", 16, "bold"),
            fg_color="transparent",
            hover_color="#1E3A5F",
            text_color="white",
            border_width=2,
            border_color="gold",
            command=self.hide_zekr,
            width=100,
            height=40
        )
        self.zekr_back_button.place(relx=0.02, rely=0.02)
        
        # إخفاء الذكر في البداية
        self.zekr_frame.place_forget()
    
    def _create_surah_widget(self):
        """إنشاء عنصر عرض السور (صفحة كاملة)"""
        # إنشاء إطار كامل الشاشة للسور
        self.surah_frame = ctk.CTkFrame(
            self.root,
            fg_color="#1A0F2E",
            corner_radius=0
        )
        self.surah_frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        # حاوية مركزية للسور
        center_frame = ctk.CTkFrame(
            self.surah_frame,
            fg_color="transparent"
        )
        center_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.8)
        
        # أيقونة القرآن
        self.surah_icon = ctk.CTkLabel(
            center_frame,
            text="📖",
            font=("Arial", 110, "bold"),
            text_color="gold"
        )
        self.surah_icon.pack(pady=(20, 10))
        
        # عنوان السور
        self.surah_main_title = ctk.CTkLabel(
            center_frame,
            text="سور الإخلاص والمعوذتين",
            font=("Arial", 55, "bold"),
            text_color="#FFD700"
        )
        self.surah_main_title.pack(pady=(0, 20))
        
        
        # نص السورة
        self.surah_label = ctk.CTkLabel(
            center_frame,
            text="",
            font=("Arial", 70),
            text_color="#E6E6FA",
            wraplength=1100,
            justify="center",
            
        )
        self.surah_label.pack(pady=20, padx=50, fill="both", expand=True)
        
        # تذييل مع معلومات التكرار
        self.surah_footer = ctk.CTkLabel(
            center_frame,
            text="",
            font=("Arial", 18),
            text_color="#87CEEB"
        )
        self.surah_footer.pack(pady=15)
        
        # زر العودة (خفيف في الزاوية)
        self.surah_back_button = ctk.CTkButton(
            self.surah_frame,
            text="العودة",
            font=("Arial", 16, "bold"),
            fg_color="transparent",
            hover_color="#2A1F3E",
            text_color="white",
            border_width=2,
            border_color="gold",
            command=self.hide_surah,
            width=100,
            height=40
        )
        self.surah_back_button.place(relx=0.02, rely=0.02)
        
        # إخفاء السور في البداية
        self.surah_frame.place_forget()

    def show_zekr(self, prayer_name):
        """عرض الأذكار بعد الصلاة"""
        if getattr(self, "skip_azkar", False):
            print("⛔ تم تعطيل عرض الأذكار لأن الوقت الحالي بعيد عن أوقات الصلاة.")
            return

        if self.zekr_visible:
            print("⛔ الأذكار معروضة بالفعل - منع التكرار")
            return  # منع التكرار إذا الأذكار معروضة بالفعل
            
        print(f"🕌 عرض الأذكار بعد صلاة {prayer_name}")
        self.zekr_visible = True
        self.current_prayer_for_azkar = prayer_name
        self.zekr_start_time = time.time()
        
        # تحديث عنوان الصلاة
        prayer_title = f"أذكار بعد صلاة {DISPLAY_NAMES[prayer_name]}"
        self.zekr_prayer_title.configure(text=prayer_title)
        
        # البدء من أول ذكر
        self.current_zekr_index = 0
        azkar_list = self.azkar_by_prayer[prayer_name]
        zekr_text = azkar_list[self.current_zekr_index]
        
        # تحديث نص الذكر
        self.zekr_label.configure(text=zekr_text)
        
        # تحديث التذييل
        self.zekr_footer.configure(text=f"الذكر {self.current_zekr_index + 1} من {len(azkar_list)} - التبديل التلقائي بعد 25 ثانية")
        
        # إظهار الإطار كامل الشاشة
        self.zekr_frame.lift()
        self.zekr_frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        # بدء التبديل التلقائي كل 25 ثانية
        self._start_zekr_rotation()
    
    def show_surah(self, prayer_name):
        """عرض السور بعد الصلاة"""
        if self.surah_visible:
            print("⛔ السور معروضة بالفعل - منع التكرار")
            return  # منع التكرار إذا السور معروضة بالفعل
            
        print(f"🕌 عرض السور بعد صلاة {prayer_name}")
        self.surah_visible = True
        self.current_prayer_for_azkar = prayer_name
        self.surah_start_time = time.time()
        
        # البدء من أول سورة
        self.current_surah_index = 0
        surah = self.surahs[self.current_surah_index]
        
        # تحديد عدد التكرارات حسب الصلاة
        repeat_count = 1
        if prayer_name in ["Fajr", "Maghrib"]:
            repeat_count = 3
        
        # تحديث نص السورة مع عدد التكرارات
        surah_text = f"{surah['title']} ({repeat_count} مرات)\n\n{surah['text']}"
        self.surah_label.configure(text=surah_text)
        
        # تحديث التذييل
        self.surah_footer.configure(
            text=f"السورة {self.current_surah_index + 1} من {len(self.surahs)} - التبديل التلقائي بعد 30 ثانية"
        )
        
        # إظهار الإطار كامل الشاشة
        self.surah_frame.lift()
        self.surah_frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        # بدء التبديل التلقائي كل 25 ثانية
        self._start_surah_rotation()

    def _start_zekr_rotation(self):
        """بدء تدوير الأذكار كل 20 ثانية"""
        if not self.zekr_visible:
            return
            
        # التبديل إلى الذكر التالي كل 25 ثانية
        self.root.after(25000, self._next_zekr)
    
    def _next_zekr(self):
        """الانتقال إلى الذكر التالي"""
        if not self.zekr_visible or not self.current_prayer_for_azkar:
            return
            
        azkar_list = self.azkar_by_prayer[self.current_prayer_for_azkar]
        
        # الانتقال إلى الذكر التالي
        self.current_zekr_index = (self.current_zekr_index + 1) % len(azkar_list)
        zekr_text = azkar_list[self.current_zekr_index]
        
        # تحديث نص الذكر
        self.zekr_label.configure(text=zekr_text)
        
        # تحديث التذييل
        self.zekr_footer.configure(text=f"الذكر {self.current_zekr_index + 1} من {len(azkar_list)} - التبديل التلقائي بعد 25 ثانية")
        
        # إذا كان هذا آخر ذكر، الانتقال إلى السور
        if self.current_zekr_index == len(azkar_list) - 1:
            # الانتقال إلى السور بعد 25 ثانية
            self.root.after(25000, self._switch_to_surah)
        else:
            # الاستمرار في تدوير الأذكار
            self._start_zekr_rotation()
    
    def _start_surah_rotation(self):
        """بدء تدوير السور كل 30 ثانية"""
        if not self.surah_visible:
            return
            
        # التبديل إلى السورة التالية كل 30 ثانية
        self.root.after(30000, self._next_surah)
    
    def _next_surah(self):
        """الانتقال إلى السورة التالية"""
        if not self.surah_visible:
            return
            
        # الانتقال إلى السورة التالية
        self.current_surah_index = (self.current_surah_index + 1) % len(self.surahs)
        
        surah = self.surahs[self.current_surah_index]
        self.surah_label.configure(text=f"{surah['title']}\n\n{surah['text']}")
        
        # تحديث التذييل
        self.surah_footer.configure(text=f"السورة {self.current_surah_index + 1} من {len(self.surahs)} - التبديل التلقائي بعد 30 ثانية")
        
        # إذا كان هذا آخر سورة، العودة للواجهة الرئيسية
        if self.current_surah_index == len(self.surahs) - 1:
            # العودة للواجهة الرئيسية بعد 25 ثانية
            self.root.after(25000, self._switch_to_main)
        else:
            # الاستمرار في تدوير السور
            self._start_surah_rotation()
    
    def _switch_to_surah(self):
        """التبديل من الأذكار إلى السور"""
        if self.zekr_visible:
            self.hide_zekr()
            if self.current_prayer_for_azkar:
                self.show_surah(self.current_prayer_for_azkar)
    
    def _switch_to_main(self):
        """التبديل من السور إلى الواجهة الرئيسية"""
        if self.surah_visible:
            self.hide_surah()
    
    def hide_zekr(self):
        """إخفاء الأذكار"""
        self.zekr_visible = False
        self.zekr_frame.place_forget()
    
    def hide_surah(self):
        """إخفاء السور والعودة للصفحة الرئيسية"""
        self.surah_visible = False
        self.current_prayer_for_azkar = None
        self.surah_frame.place_forget()
    
    def _get_prayer_time_today(self, prayer_name):
        """الحصول على وقت الصلاة الحالي كـ datetime"""
        today_times = self.prayer_times.get_today_times()
        if not today_times or prayer_name not in today_times:
            return None
        
        prayer_time_str = today_times[prayer_name]
        if not prayer_time_str or prayer_time_str == "--:--":
            return None
        
        try:
            # تحويل الوقت من نص إلى datetime
            now = datetime.datetime.now()
            hour, minute = map(int, prayer_time_str.split(':'))
            prayer_time = datetime.datetime(now.year, now.month, now.day, hour, minute)
            return prayer_time
        except ValueError:
            return None
    
    def update_display(self):
        """تحديث العرض"""
        now = datetime.datetime.now()
        
        # التاريخ الميلادي والهجري
        # استخراج اليوم العربي من البيانات إذا كان متوفراً
        today_times = self.prayer_times.get_today_times()
        arabic_day = today_times.get('ArabicDay', '')
        
        if not arabic_day:
            # إذا لم يكن اليوم العربي متوفراً في البيانات، نستخدم القائمة الافتراضية
            weekday_ar = ["الاثنين","الثلاثاء","الأربعاء","الخميس","الجمعة","السبت","الأحد"]
            arabic_day = weekday_ar[now.weekday()]
        
        # التاريخ الهجري
        hijri_date = self.prayer_times.get_hijri_date()
        
        # تنسيق التاريخ الكامل
        full_date = f"{arabic_day}،  {now.day}/{now.month}/{now.year}  -  {now.strftime('%H:%M:%S')}"
        
        self.date_label.configure(text=full_date)
        
        # تحديث الثيم
        self.theme_manager.update_theme()
        
        # تحديث أوقات الصلاة
        if today_times:
            for prayer, time_label in self.prayer_columns:
                time_label.configure(text=today_times.get(prayer, "--:--"))
        else:
            for _, time_label in self.prayer_columns:
                time_label.configure(text="--:--")

        # تحديث وقت الشروق
        sunrise_time = self.prayer_times.get_sunrise_time()
        self.sunrise_time.configure(text=sunrise_time)
        
        # تحديث وقت صلاة الجمعة (نفس وقت الظهر في يوم الجمعة) - التصحيح هنا
        jumaa_time = today_times.get('Dhuhr', '12:30')  # دائماً نستخدم وقت الظهر
        self.jumaa_time.configure(text=jumaa_time)

        # تحديث الصلاة القادمة والتحقق من الأذكار
        self.update_next_prayer()
        
        # التحقق من جدول الجمعة الخاص
        self._check_jumaa_schedule()
        
        # التحقق من عرض الأذكار بعد الصلوات
        self._check_azkar_display()

        
    def _check_azkar_display(self):
        """التحقق من وقت عرض الأذكار بعد الصلوات"""
        now = datetime.datetime.now()
        
        # إذا كان اليوم جمعة، لا نعرض الأذكار العادية للظهر
        if now.weekday() == 4:  # 4 = الجمعة
            return  # تخطي التحقق في يوم الجمعة
        
        if getattr(self, "zekr_visible", False):
            return  # إذا الأذكار معروضة بالفعل

        for prayer_name in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
            prayer_time = self._get_prayer_time_today(prayer_name)
            if not prayer_time:
                continue
            
            # الوقت بعد الصلاة + IQAMA_DELAY + الوقت الإضافي للأذكار
            azkar_start_time = prayer_time + datetime.timedelta(seconds=self.azkar_times[prayer_name])
            azkar_end_time = azkar_start_time + datetime.timedelta(minutes=30)
            
            # إذا الوقت الحالي داخل فترة الأذكار ولم يتم عرضها بعد
            if azkar_start_time <= now <= azkar_end_time and getattr(self, "last_prayer_completed", None) != prayer_name:
                self.show_zekr(prayer_name)
                self.last_prayer_completed = prayer_name
                print(f"⏳ عرض أذكار بعد صلاة {prayer_name}")
                break
    
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