# prayer_times.py
import datetime
from config import DISPLAY_NAMES

class PrayerTimes:
    def __init__(self, csv_data):
        self.data = csv_data
    
    def find_next_prayer(self):
        """إيجاد الصلاة القادمة"""
        now = datetime.datetime.now()
        today_str = now.strftime("%m-%d")

        # البحث عن اليوم الحالي
        day = None
        for date, times in self.data.items():
            if date[5:] == today_str:
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

        # إذا مرّت كل الصلوات، خذ فجر الغد
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
    
    def get_today_times(self):
        """الحصول على أوقات الصلاة لليوم"""
        today_str = datetime.datetime.now().strftime("%m-%d")
        
        for date, times in self.data.items():
            if date[5:] == today_str:
                return times
        
        return None
    
    def get_prayer_display_name(self, prayer_key):
        """الحصول على الاسم المعروض للصلاة"""
        return DISPLAY_NAMES.get(prayer_key, prayer_key)