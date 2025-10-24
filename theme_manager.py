# theme_manager.py
import datetime
import customtkinter as ctk
from config import THEME_COLORS

class ThemeManager:
    def __init__(self):
        self.current_theme = self.get_current_theme()
        ctk.set_appearance_mode(self.current_theme)
    
    def get_current_theme(self):
        """تحديد الثيم بناءً على الوقت الحالي"""
        now = datetime.datetime.now()
        hour = now.hour
        
        if 6 <= hour < 18:
            return "light"  # النهاري
        else:
            return "dark"   # الليلي
    
    def update_theme(self):
        """تحديث الثيم إذا تغير الوقت"""
        new_theme = self.get_current_theme()
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            ctk.set_appearance_mode(new_theme)
            print(f"🕋 تغيير الثيم إلى: {'نهاري' if new_theme == 'light' else 'ليلي'}")
            return True
        return False
    
    def get_colors(self):
        """الحصول على ألوان الثيم الحالي"""
        return THEME_COLORS.get(self.current_theme, THEME_COLORS["dark"])