# audio_manager.py
import threading
import os
from playsound import playsound
from config import resource_path, ADHAN_FILE, IQAMA_FILE

class AudioManager:
    def __init__(self):
        self.currently_playing = None
    
    def play_adhan(self):
        """تشغيل صوت الأذان"""
        adhan_file = resource_path(ADHAN_FILE)
        if os.path.exists(adhan_file):
            self.currently_playing = "adhan"
            threading.Thread(target=lambda: self._play_sound(adhan_file), daemon=True).start()
    
    def play_iqama(self):
        """تشغيل صوت الإقامة"""
        iqama_file = resource_path(IQAMA_FILE)
        if os.path.exists(iqama_file):
            self.currently_playing = "iqama"
            threading.Thread(target=lambda: self._play_sound(iqama_file), daemon=True).start()
    
    def _play_sound(self, file_path):
        """تشغيل الصوت في thread منفصل"""
        try:
            playsound(file_path, block=True)
        except Exception as e:
            print(f"خطأ في تشغيل الصوت: {e}")
        finally:
            self.currently_playing = None
    
    def is_playing(self):
        """التحقق إذا كان هناك صوت يشغل حالياً"""
        return self.currently_playing is not None