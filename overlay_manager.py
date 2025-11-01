import customtkinter as ctk
import datetime
from config import IQAMA_DELAY, DISPLAY_NAMES


class OverlayManager:
    def __init__(self, root, font_scales, audio_manager):
        self.root = root
        self.font_scales = font_scales
        self.audio_manager = audio_manager
        
        # إنشاء overlay
        self.overlay = ctk.CTkFrame(root, fg_color="#0A1F3A")
        self.overlay.place(relwidth=1, relheight=1)
        
        self.animation_running = False
        self.current_prayer_for_iqama = None
        self.iqama_countdown_time = 0
        
        # متغيرات لتتبع العناصر الحالية
        self.current_iqama_icon = None
        self.current_overlay_label = None
        self.current_overlay_countdown = None
        self.current_iqama_text = None
        
        self._create_overlay_widgets()
        self.overlay.lower()
    
    def _create_overlay_widgets(self):
        """إنشاء عناصر الـ overlay"""
        # تنظيف أي عناصر موجودة مسبقاً
        self._cleanup_overlay_widgets()
        
        overlay_container = ctk.CTkFrame(self.overlay, fg_color="transparent")
        overlay_container.pack(expand=True)
        
        # أيقونة متحركة للإقامة
        self.current_iqama_icon = ctk.CTkLabel(
            overlay_container,
            text="",
            font=("Arial", self.font_scales['overlay_icon_font'], "bold"),
            text_color="gold" 
        )
        self.current_iqama_icon.pack(pady=20)
        
        self.current_overlay_label = ctk.CTkLabel(
            overlay_container,
            text="",
            font=("Arial", self.font_scales['overlay_text_font'], "bold"),
            text_color="gold"  
        )
        self.current_overlay_label.pack(pady=10)
        
        self.current_overlay_countdown = ctk.CTkLabel(
            overlay_container,
            text="",
            font=("Arial", self.font_scales['overlay_countdown_font'], "bold"),
            text_color="#00FFFF"
        )
        self.current_overlay_countdown.pack(pady=10)
    
    def _cleanup_overlay_widgets(self):
        """تنظيف جميع عناصر الـ overlay"""
        self.stop_animation()
        
        # تنظيف جميع العناصر الموجودة في الـ overlay
        for widget in self.overlay.winfo_children():
            widget.destroy()
        
        # إعادة تعيين المؤشرات
        self.current_iqama_icon = None
        self.current_overlay_label = None
        self.current_overlay_countdown = None
        self.current_iqama_text = None
    
    def show_adhan_overlay(self, prayer_name):
        """عرض شاشة الأذان"""
        print(f"بدأ الأذان لصلاة {prayer_name}")
        
        # تنظيف العناصر القديمة أولاً
        self._cleanup_overlay_widgets()
        self._create_overlay_widgets()
        
        # تحديث النصوص
        self.current_overlay_label.configure(text=f"🕌 أذان {DISPLAY_NAMES[prayer_name]} ")
        if self.current_iqama_icon:
            self.current_iqama_icon.configure(text="", font=("Arial", self.font_scales['overlay_icon_font'], "bold"))
        if self.current_overlay_countdown:
            self.current_overlay_countdown.configure(text="")
        
        self.overlay.lift()
        
        # تشغيل الأذان
        self.audio_manager.play_adhan()
        
        # حفظ الصلاة الحالية للإقامة
        self.current_prayer_for_iqama = prayer_name
        
        # حساب وقت الإقامة - استخدم وقت الجمعة الخاص إذا كان اليوم جمعة
        now = datetime.datetime.now()
        is_jumaa = (now.weekday() == 4 and prayer_name == "Dhuhr")
        
        if is_jumaa:
            iqama_delay_minutes = 1  # 1 دقيقة فقط للجمعة
            print(f"🕌 اليوم جمعة - سيتم الإقامة بعد {iqama_delay_minutes} دقيقة")
            
            # للجمعة، لا نبدأ العد التنازلي للإقامة - سيتم التعامل معها في نظام الجمعة
            return  # إرجاع مبكر للجمعة
        else:
            iqama_delay_minutes = IQAMA_DELAY.get(prayer_name, 1)
            print(f"سيتم الإقامة بعد {iqama_delay_minutes} دقائق")
        
        # بدء شاشة الإقامة بعد دقيقة (لغير الجمعة فقط)
        self.root.after(60 * 1000, lambda: self._start_iqama_countdown(prayer_name, iqama_delay_minutes, is_jumaa))

    def _start_iqama_countdown(self, prayer_name, total_minutes, is_jumaa=False):
        """بدء العد التنازلي للإقامة"""
        print(f"بدأ العد التنازلي للإقامة: {total_minutes} دقائق")

        # تنظيف العناصر القديمة أولاً
        self._cleanup_overlay_widgets()

        self.current_prayer_for_iqama = prayer_name
        self.iqama_countdown_time = total_minutes * 60

        # الأيقونة المتحركة
        self.current_iqama_icon = ctk.CTkLabel(
            self.overlay,
            text="🕌",
            font=("Arial", self.font_scales['overlay_icon_font'], "bold"),
            text_color="gold"
        )
        self.current_iqama_icon.place(relx=0.5, rely=0.35, anchor="center")

        # Frame للنص والعداد
        text_frame = ctk.CTkFrame(self.overlay, fg_color="#0A1F3A")
        text_frame.place(relx=0.5, rely=0.7, anchor="center")

        # النص الثابت - إضافة مؤشر الجمعة إذا كان يوم جمعة
        prayer_text = f"إقامة صلاة {DISPLAY_NAMES[prayer_name]}"
        if is_jumaa:
            prayer_text += " (الجمعة)"
        
        self.current_iqama_text = ctk.CTkLabel(
            text_frame,
            text=prayer_text,
            font=("Arial", self.font_scales['overlay_text_font'], "bold"),
            text_color="white"
        )
        self.current_iqama_text.pack(pady=(0, 15))

        # العد التنازلي
        self.current_overlay_countdown = ctk.CTkLabel(
            text_frame,
            text="",
            font=("Arial", self.font_scales['overlay_countdown_font'], "bold"),
            text_color="#00FFFF"
        )
        self.current_overlay_countdown.pack()

        # رفع الـ overlay
        self.overlay.lift()

        # بدء التحريك والعد التنازلي
        self.animation_running = True
        self._animate_iqama_icon()
        self._update_iqama_countdown()
    
    def play_iqama_directly(self, prayer_name):
        """تشغيل الإقامة مباشرة (لنظام الجمعة)"""
        print(f"🕌 تشغيل الإقامة مباشرة لصلاة {prayer_name}")
        
        # تنظيف أي overlay موجود
        self._cleanup_overlay_widgets()
        
        # تشغيل صوت الإقامة
        # self.audio_manager.play_iqama()
        
        # عرض رسالة الإقامة
        self._create_overlay_widgets()
        self.current_overlay_label.configure(text=f"🕌 إقامة صلاة الجمعة")
        
        # أيقونة المسجد
        if self.current_iqama_icon:
            self.current_iqama_icon.configure(text="🕌", font=("Arial", self.font_scales['overlay_icon_font'], "bold"))
        
        # نص توجيهي
        if self.current_overlay_countdown:
            self.current_overlay_countdown.configure(text="يرجى إطفاء الهواتف")
        
        self.overlay.lift()
        
        # إخفاء الـ overlay بعد 15 ثانية
        self.root.after(15000, self.hide_overlay)
        
    def _animate_iqama_icon(self, size=None, growing=True):
        """تحريك أيقونة الإقامة"""
        if not self.animation_running:
            return

        # التحقق من وجود العنصر قبل التعديل
        if not self.current_iqama_icon or not self.current_iqama_icon.winfo_exists():
            self.animation_running = False
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

        self.current_iqama_icon.configure(font=("Arial", size, "bold"))

        if self.overlay.winfo_ismapped() and self.animation_running:
            self.root.after(200, lambda: self._animate_iqama_icon(size, growing))
    
    def _update_iqama_countdown(self):
        """تحديث العد التنازلي للإقامة"""
        # التحقق من وجود العناصر قبل التحديث
        if not self.current_overlay_countdown or not self.current_overlay_countdown.winfo_exists():
            return

        if self.iqama_countdown_time > 0:
            minutes = self.iqama_countdown_time // 60
            seconds = self.iqama_countdown_time % 60
            
            self.current_overlay_countdown.configure(text=f"{minutes:02d}:{seconds:02d}")
            self.iqama_countdown_time -= 1
            self.root.after(1000, self._update_iqama_countdown)
        else:
            self._play_iqama_sound()
    
    def _play_iqama_sound(self):
        """تشغيل صوت الإقامة"""
        if self.current_prayer_for_iqama:
            print(f"تشغيل صوت الإقامة لصلاة {self.current_prayer_for_iqama}")
            
            self.stop_animation()
            # self.audio_manager.play_iqama()
            
            # التحقق من وجود العنصر قبل التحديث
            if self.current_overlay_countdown and self.current_overlay_countdown.winfo_exists():
                self.current_overlay_countdown.configure(text="إطفئ الهاتف")
            
            self.root.after(15 * 1000, self.hide_overlay)
            self.current_prayer_for_iqama = None
    
    def stop_animation(self):
        """إيقاف تحريك الأيقونة"""
        self.animation_running = False
    
    def hide_overlay(self):
        """إخفاء الـ overlay"""
        self._cleanup_overlay_widgets()
        self.overlay.lower()
        self.stop_animation()

    def stop_iqama_countdown(self):
        """إيقاف العد التنازلي للإقامة"""
        self.stop_animation()
        self._cleanup_overlay_widgets()
        self.overlay.lower()
        print("⏹️ إيقاف العد التنازلي للإقامة")