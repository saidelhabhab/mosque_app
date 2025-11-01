Mosque Prayer Display App (Morocco)
-----------------------------------

📖 Usage:
1. Open a terminal or CMD.
2. Navigate to this folder:
   cd Mosque-Prayer-Display
3. Run the app:
   python mosque_display_full.py

🕌 Features:
- Fullscreen display for TV or projector.
- Shows next prayer and countdown.
- Reads prayer_times.csv for any day.
- Press ESC to exit fullscreen.

You can edit prayer_times.csv to add more dates or adjust times.

Made for Moroccan Mosques 🇲🇦

when exe <----------- exe ------------------->
python -m PyInstaller --onefile --windowed --icon=mosque.ico --add-data "background.jpg;." --add-data "adhan.wav;." --add-data "close.png;." --add-data "minimize.png;." --add-data "meknes_prayer_all.csv;." --add-data "mosque.ico;." mosque_app.py



site de <i class="fa fa-download" aria-hidden="true"></i> ==> https://aladhan.com/calendar/Gare%20de%20Mekn%C3%A8s/Morocco#