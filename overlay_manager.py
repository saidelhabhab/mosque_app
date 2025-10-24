# overlay_manager.py
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
        
        self._create_overlay_widgets()
        self.overlay.lower()
    
    def _create_overlay_widgets(self):
        """إنشاء عناصر الـ overlay"""
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
            text_color="#00FFFF"
        )
        self.overlay_countdown.pack(pady=10)
    
    def show_adhan_overlay(self, prayer_name):
        """عرض شاشة الأذان"""
        print(f"بدأ الأذان لصلاة {prayer_name}")
        self.overlay_label.configure(text=f"🕌 أذان {DISPLAY_NAMES[prayer_name]} ")
        self.iqama_icon.configure(text="", font=("Arial", self.font_scales['overlay_icon_font'], "bold"))
        self.overlay_countdown.configure(text="")
        self.overlay.lift()
        
        # تشغيل الأذان
        self.audio_manager.play_adhan()
        
        # حفظ الصلاة الحالية للإقامة
        self.current_prayer_for_iqama = prayer_name
        
        # حساب وقت الإقامة
        iqama_delay_minutes = IQAMA_DELAY.get(prayer_name, 1)
        print(f"سيتم الإقامة بعد {iqama_delay_minutes} دقائق")
        
        # بدء شاشة الإقامة بعد دقيقة
        self.root.after(60 * 1000, lambda: self._start_iqama_countdown(prayer_name, iqama_delay_minutes))
    
    def _start_iqama_countdown(self, prayer_name, total_minutes):
        """بدء العد التنازلي للإقامة"""
        print(f"بدأ العد التنازلي للإقامة: {total_minutes} دقائق")

        self.current_prayer_for_iqama = prayer_name
        self.iqama_countdown_time = total_minutes * 60

        # تنظيف الشاشة القديمة
        self.overlay.lift()
        for widget in self.overlay.winfo_children():
            widget.destroy()

        # الأيقونة المتحركة
        self.iqama_icon = ctk.CTkLabel(
            self.overlay,
            text="🕌",
            font=("Arial", self.font_scales['overlay_icon_font'], "bold"),
            text_color="gold"
        )
        self.iqama_icon.place(relx=0.5, rely=0.35, anchor="center")

        # Frame للنص والعداد
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

        # العد التنازلي
        self.overlay_countdown = ctk.CTkLabel(
            text_frame,
            text="",
            font=("Arial", self.font_scales['overlay_countdown_font'], "bold"),
            text_color="#00FFFF"
        )
        self.overlay_countdown.pack()

        # بدء التحريك والعد التنازلي
        self.animation_running = True
        self._animate_iqama_icon()
        self._update_iqama_countdown()
    
    def _animate_iqama_icon(self, size=None, growing=True):
        """تحريك أيقونة الإقامة"""
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
            self.root.after(200, lambda: self._animate_iqama_icon(size, growing))
    
    def _update_iqama_countdown(self):
        """تحديث العد التنازلي للإقامة"""
        if self.iqama_countdown_time > 0:
            minutes = self.iqama_countdown_time // 60
            seconds = self.iqama_countdown_time % 60
            
            self.overlay_countdown.configure(text=f"{minutes:02d}:{seconds:02d}")
            self.iqama_countdown_time -= 1
            self.root.after(1000, self._update_iqama_countdown)
        else:
            self._play_iqama_sound()
    
    def _play_iqama_sound(self):
        """تشغيل صوت الإقامة"""
        if self.current_prayer_for_iqama:
            print(f"تشغيل صوت الإقامة لصلاة {self.current_prayer_for_iqama}")
            
            self.stop_animation()
            self.audio_manager.play_iqama()
            
            self.overlay_countdown.configure(text="إطفئ الهاتف")
            self.root.after(15 * 1000, self.hide_overlay)
            self.current_prayer_for_iqama = None
    
    def stop_animation(self):
        """إيقاف تحريك الأيقونة"""
        self.animation_running = False
        if hasattr(self, "iqama_icon") and self.iqama_icon.winfo_exists():
            self.iqama_icon.configure(font=("Arial", self.font_scales['overlay_icon_font'], "bold"))
    
    def hide_overlay(self):
        """إخفاء الـ overlay"""
        self.overlay.lower()
        self.stop_animation()