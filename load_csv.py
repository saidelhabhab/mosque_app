import csv
import datetime

def convert_prayer_times_to_simple_format(input_files, output_file):
    """تحويل بيانات الصلوات من التنسيق المفصل إلى التنسيق المبسط مع تعديل التوقيت"""
    
    all_data = []
    
    for input_file in input_files:
        print(f"جاري معالجة: {input_file}")
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f_in:
                reader = csv.DictReader(f_in)
                
                for row in reader:
                    date_raw = row.get('date.readable', '').strip()
                    if not date_raw:
                        continue

                    try:
                        # تحويل التاريخ من "01 Jan 2026" إلى "2026-01-01"
                        dt = datetime.datetime.strptime(date_raw, "%d %b %Y")
                        
                        # دالة لتحويل الوقت من GMT+1 إلى GMT+0 (طرح ساعة)
                        def convert_time_gmt(time_str):
                            if not time_str:
                                return ""
                            
                            # نأخذ الجزء الأول فقط (مثال: "06:53" من "06:53 (+01)")
                            time_part = time_str.split(' ')[0].strip()
                            
                            if not time_part or time_part == "--:--":
                                return ""
                            
                            try:
                                # تحويل الوقت إلى كائن datetime
                                hour, minute = map(int, time_part.split(':'))
                                time_dt = datetime.datetime(dt.year, dt.month, dt.day, hour, minute)
                                
                                # طرح ساعة واحدة (من GMT+1 إلى GMT+0)
                                time_dt = time_dt - datetime.timedelta(hours=1)
                                
                                return time_dt.strftime("%H:%M")
                                
                            except ValueError:
                                return time_part  # إذا كان هناك خطأ في التحويل، نرجع الوقت كما هو
                        
                        # استخراج الأوقات مع التحويل
                        fajr = convert_time_gmt(row.get("timings.Fajr", ""))
                        sunrise = convert_time_gmt(row.get("timings.Sunrise", ""))
                        dhuhr = convert_time_gmt(row.get("timings.Dhuhr", ""))
                        asr = convert_time_gmt(row.get("timings.Asr", ""))
                        maghrib = convert_time_gmt(row.get("timings.Maghrib", ""))
                        isha = convert_time_gmt(row.get("timings.Isha", ""))
                        imsak = convert_time_gmt(row.get("timings.Imsak", ""))
                        midnight = convert_time_gmt(row.get("timings.Midnight", ""))
                        
                        # استخراج اليوم العربي
                        weekday_ar = row.get('date.hijri.weekday.ar', '')
                        
                        # استخراج التاريخ الهجري
                        hijri_date = row.get('date.hijri.date', '')
                        hijri_day = row.get('date.hijri.day', '')
                        hijri_month_ar = row.get('date.hijri.month.ar', '')
                        hijri_year = row.get('date.hijri.year', '')
                        
                        # تنسيق التاريخ الهجري
                        hijri_formatted = f"{hijri_day}/{hijri_month_ar}/{hijri_year}" if hijri_day and hijri_month_ar and hijri_year else ""
                        
                        # إنشاء الصف الجديد مع البيانات الإضافية
                        new_row = {
                            "تاريخ": dt.strftime("%Y-%m-%d"),
                            "الفجر": fajr,
                            "الشروق": sunrise,
                            "الظهر": dhuhr,
                            "العصر": asr,
                            "المغرب": maghrib,
                            "العشاء": isha,
                            "الإمساك": imsak,
                            "منتصف الليل": midnight,
                            "اليوم العربي": weekday_ar,
                            "التاريخ الهجري": hijri_formatted,
                            "اليوم الهجري": hijri_day,
                            "الشهر الهجري": hijri_month_ar,
                            "السنة الهجرية": hijri_year,
                            "place": "مدينة مكناس - المغرب"
                        }
                        
                        all_data.append(new_row)
                        
                    except ValueError as e:
                        print(f"خطأ في تحليل التاريخ {date_raw}: {e}")
                        continue
                        
        except Exception as e:
            print(f"خطأ في قراءة الملف {input_file}: {e}")
    
    # حفظ البيانات في ملف واحد
    if all_data:
        with open(output_file, 'w', newline='', encoding='utf-8') as f_out:
            fieldnames = [
                "تاريخ", "الفجر", "الشروق", "الظهر", "العصر", 
                "المغرب", "العشاء", "الإمساك", "منتصف الليل",
                "اليوم العربي", "التاريخ الهجري", "اليوم الهجري", 
                "الشهر الهجري", "السنة الهجرية", "place"
            ]
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_data)
        
        print(f"✅ تم إنشاء ملف {output_file} يحتوي على {len(all_data)} يوم")
        print("🕐 تم تحويل جميع الأوقات من GMT+1 إلى GMT+0")
        print("📊 الأعمدة المضافة:")
        print("   - الفجر (Fajr)")
        print("   - الشروق (Sunrise)")
        print("   - الظهر (Dhuhr)")
        print("   - العصر (Asr)")
        print("   - المغرب (Maghrib)")
        print("   - العشاء (Isha)")
        print("   - الإمساك (Imsak)")
        print("   - منتصف الليل (Midnight)")
        print("   - اليوم العربي")
        print("   - التاريخ الهجري الكامل")
        print("   - اليوم الهجري")
        print("   - الشهر الهجري")
        print("   - السنة الهجرية")
        
        # عرض مثال على التحويل
        if all_data:
            sample = all_data[0]
            print("\n📋 مثال على البيانات المحولة:")
            print(f"   التاريخ: {sample['تاريخ']}")
            print(f"   الفجر: {sample['الفجر']} (GMT+0)")
            print(f"   الشروق: {sample['الشروق']} (GMT+0)")
            print(f"   الظهر: {sample['الظهر']} (GMT+0)")
            print(f"   المغرب: {sample['المغرب']} (GMT+0)")
            print(f"   التاريخ الهجري: {sample['التاريخ الهجري']}")
            
    else:
        print("❌ لم يتم العثور على بيانات لتحويلها")

# استخدام الكود
if __name__ == "__main__":
    input_files = [
        r"C:\Users\saidt\Desktop\mosque_app 26-10\meknes_prayer_2025.csv",
        r"C:\Users\saidt\Desktop\mosque_app 26-10\meknes_prayer_2026.csv", 
        r"C:\Users\saidt\Desktop\mosque_app 26-10\meknes_prayer_2027.csv",
        r"C:\Users\saidt\Desktop\mosque_app 26-10\meknes_prayer_2028.csv",
        r"C:\Users\saidt\Desktop\mosque_app 26-10\meknes_prayer_2029.csv",
        r"C:\Users\saidt\Desktop\mosque_app 26-10\meknes_prayer_2030.csv"
    ]
    
    output_file = r"C:\Users\saidt\Desktop\mosque_app 26-10\meknes_prayer_all.csv"
    
    convert_prayer_times_to_simple_format(input_files, output_file)