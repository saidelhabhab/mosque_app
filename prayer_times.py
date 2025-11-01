import csv
import datetime
import os
from config import CSV_FILE, DISPLAY_NAMES

class PrayerTimes:
    def __init__(self, csv_data):
        self.csv_data = csv_data
        self.prayer_data = self._parse_csv_data()
    
    def _parse_csv_data(self):
        """تحليل بيانات CSV بالتنسيق المبسط مع البيانات الإضافية"""
        prayer_data = {}
        
        for row in self.csv_data:
            try:
                # إذا كان row عبارة عن سلسلة نصية (من CSV مباشرة)
                if isinstance(row, str):
                    continue  # تخطي السلاسل النصية
                
                # استخراج التاريخ من العمود "تاريخ"
                date_str = row.get('تاريخ', '').strip()
                if not date_str:
                    continue
                
                # تحويل التاريخ من "2025-01-01" إلى كائن date
                date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                
                # استخراج أوقات الصلوات الأساسية
                prayer_times = {
                    'Fajr': row.get('الفجر', '--:--').strip(),
                    'Dhuhr': row.get('الظهر', '--:--').strip(),
                    'Asr': row.get('العصر', '--:--').strip(), 
                    'Maghrib': row.get('المغرب', '--:--').strip(),
                    'Isha': row.get('العشاء', '--:--').strip(),
                    
                    # الأوقات الإضافية
                    'Sunrise': row.get('الشروق', '--:--').strip(),
                    'Imsak': row.get('الإمساك', '--:--').strip(),
                    'Midnight': row.get('منتصف الليل', '--:--').strip(),
                    
                    # البيانات الهجرية
                    'HijriDate': row.get('التاريخ الهجري', '').strip(),
                    'HijriDay': row.get('اليوم الهجري', '').strip(),
                    'HijriMonth': row.get('الشهر الهجري', '').strip(),
                    'HijriYear': row.get('السنة الهجرية', '').strip(),
                    'ArabicDay': row.get('اليوم العربي', '').strip()
                }
                
                # التحقق من صحة الأوقات
                for prayer in ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha', 'Sunrise', 'Imsak', 'Midnight']:
                    if not self._is_valid_time(prayer_times[prayer]):
                        prayer_times[prayer] = '--:--'
                
                # إضافة البيانات
                prayer_data[date_obj] = prayer_times
                
            except (ValueError, KeyError) as e:
                print(f"خطأ في تحليل سطر: {row}. الخطأ: {e}")
                continue
        
        print(f"تم تحميل {len(prayer_data)} يوم من بيانات الصلوات")
        return prayer_data
    
    def _is_valid_time(self, time_str):
        """التحقق من صيغة الوقت"""
        if not time_str or time_str == '--:--':
            return False
        
        try:
            if ':' in time_str:
                parts = time_str.split(':')
                if len(parts) == 2:
                    hour, minute = int(parts[0]), int(parts[1])
                    return 0 <= hour <= 23 and 0 <= minute <= 59
            return False
        except ValueError:
            return False
    
    def get_today_times(self):
        """الحصول على أوقات الصلوات لليوم الحالي"""
        today = datetime.date.today()
        return self.prayer_data.get(today, {})
    
    def get_hijri_date(self):
        """الحصول على التاريخ الهجري لليوم الحالي"""
        today = datetime.date.today()
        today_data = self.prayer_data.get(today, {})
        
        hijri_date = today_data.get('HijriDate', '')
        if hijri_date:
            return hijri_date
        else:
            # إذا لم يكن التاريخ الهجري متوفراً، نرجع تاريخ افتراضي
            return "١٤٤٧/٠٧/١٢"
    
    def get_sunrise_time(self):
        """الحصول على وقت الشروق لليوم الحالي"""
        today = datetime.date.today()
        today_data = self.prayer_data.get(today, {})
        return today_data.get('Sunrise', '--:--')
    
    def get_imsak_time(self):
        """الحصول على وقت الإمساك لليوم الحالي"""
        today = datetime.date.today()
        today_data = self.prayer_data.get(today, {})
        return today_data.get('Imsak', '--:--')
    
    def find_next_prayer(self):
        """إيجاد الصلاة القادمة"""
        now = datetime.datetime.now()
        today = now.date()
        
        # الحصول على أوقات اليوم
        today_times = self.get_today_times()
        if not today_times:
            return None, None
        
        # ترتيب الصلوات حسب وقتها
        prayers_order = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
        
        for prayer in prayers_order:
            prayer_time_str = today_times.get(prayer)
            if not prayer_time_str or prayer_time_str == "--:--":
                continue
            
            try:
                # تحويل وقت الصلاة إلى كائن datetime
                hour, minute = map(int, prayer_time_str.split(':'))
                prayer_dt = datetime.datetime(today.year, today.month, today.day, hour, minute)
                
                # إذا كان وقت الصلاة لم يأت بعد
                if prayer_dt > now:
                    return prayer, prayer_dt
                    
            except ValueError:
                continue
        
        # إذا مرت جميع صلوات اليوم، نعود للصلاة الأولى في اليوم التالي
        tomorrow = today + datetime.timedelta(days=1)
        tomorrow_times = self.prayer_data.get(tomorrow, {})
        
        if tomorrow_times:
            for prayer in prayers_order:
                prayer_time_str = tomorrow_times.get(prayer)
                if not prayer_time_str or prayer_time_str == "--:--":
                    continue
                
                try:
                    hour, minute = map(int, prayer_time_str.split(':'))
                    prayer_dt = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, hour, minute)
                    return prayer, prayer_dt
                except ValueError:
                    continue
        
        return None, None
    
    def get_prayer_display_name(self, prayer_key):
        """الحصول على الاسم المعروض للصلاة"""
        return DISPLAY_NAMES.get(prayer_key, prayer_key)

# احذف دالة load_csv من هنا نهائياً