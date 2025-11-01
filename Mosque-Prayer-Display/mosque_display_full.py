#!/usr/bin/env python3
# mosque_display_full.py
# Multi-day Mosque Prayer Display (Tkinter)

import tkinter as tk
from tkinter import font, filedialog, ttk, messagebox
import datetime, csv, os

CSV_FILE = "prayer_times.csv"
REFRESH_INTERVAL_MS = 1000

DISPLAY_NAMES = {
    "Fajr": "Sbah (Fajr)",
    "Dhuhr": "Dohr (Dhuhr)",
    "Asr": "Asr",
    "Maghrib": "Maghrib",
    "Isha": "Isha"
}

def load_csv(file_path=CSV_FILE):
    data = {}
    place = ""
    if not os.path.exists(file_path):
        return data, place
    try:
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(line for line in f if not line.strip().startswith('#'))
            for row in reader:
                d = row.get('date') or row.get('Date')
                if not d:
                    continue
                data[d] = {
                    "Fajr": row.get('Fajr','').strip(),
                    "Dhuhr": row.get('Dhuhr','').strip(),
                    "Asr": row.get('Asr','').strip(),
                    "Maghrib": row.get('Maghrib','').strip(),
                    "Isha": row.get('Isha','').strip()
                }
                if 'place' in row and row['place'].strip():
                    place = row['place'].strip()
    except Exception as e:
        print("CSV load error:", e)
    return data, place

class MosqueApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mosque Prayer Display - Morocco")
        self.root.configure(bg="black")
        self.root.attributes("-fullscreen", True)
        self.full = True
        self.root.bind("<Escape>", lambda e: self.toggle_fullscreen())

        # Fonts
        self.big_font = font.Font(family="Helvetica", size=72, weight="bold")
        self.medium_font = font.Font(family="Helvetica", size=36)
        self.small_font = font.Font(family="Helvetica", size=20)

        # Place & Date
        self.place_label = tk.Label(root, text="", font=self.medium_font, bg="black", fg="white")
        self.place_label.pack(anchor="n")

        self.date_label = tk.Label(root, text="", font=self.small_font, bg="black", fg="white")
        self.date_label.pack(anchor="n", pady=(0,8))

        # Center next prayer
        center = tk.Frame(root, bg="black")
        center.pack(expand=True)

        self.next_title = tk.Label(center, text="Lsalah jaya:", font=self.medium_font, bg="black", fg="yellow")
        self.next_title.pack()

        self.next_name = tk.Label(center, text="", font=self.big_font, bg="black", fg="white")
        self.next_name.pack()

        self.countdown = tk.Label(center, text="", font=self.medium_font, bg="black", fg="cyan")
        self.countdown.pack()

        # Schedule list
        schedule_frame = tk.Frame(root, bg="black")
        schedule_frame.pack(side="bottom", pady=20)

        self.schedule_title = tk.Label(schedule_frame, text="Lwa9t dyal nhar", font=self.small_font, bg="black", fg="white")
        self.schedule_title.grid(row=0, column=0, columnspan=2)

        self.rows = []
        for i in range(5):
            name_lbl = tk.Label(schedule_frame, text="", font=self.small_font, bg="black", fg="white")
            time_lbl = tk.Label(schedule_frame, text="", font=self.small_font, bg="black", fg="white")
            name_lbl.grid(row=i+1, column=0, sticky="w", padx=12)
            time_lbl.grid(row=i+1, column=1, sticky="e", padx=12)
            self.rows.append((name_lbl, time_lbl))

        # Load data
        self.data, self.place = load_csv(CSV_FILE)
        self.current_date = datetime.date.today()
        self.update_display()

        # periodic tick
        self.root.after(REFRESH_INTERVAL_MS, self.tick)

    def toggle_fullscreen(self):
        self.full = not self.full
        self.root.attributes("-fullscreen", self.full)

    def update_display(self):
        dstr = self.current_date.strftime("%Y-%m-%d")
        day = self.data.get(dstr)
        now = datetime.datetime.now()
        self.date_label.config(text=self.current_date.strftime("%A, %d %B %Y") + "    " + now.strftime("%H:%M:%S"))
        self.place_label.config(text=self.place if self.place else "(makaynch place)")

        if day:
            for i, key in enumerate(["Fajr","Dhuhr","Asr","Maghrib","Isha"]):
                name = DISPLAY_NAMES.get(key, key)
                timestr = day.get(key,"--:--")
                self.rows[i][0].config(text=name)
                self.rows[i][1].config(text=timestr)
        self.update_next_prayer()

    def find_next_prayer(self):
        dstr = self.current_date.strftime("%Y-%m-%d")
        day = self.data.get(dstr)
        if not day:
            return None, None
        now = datetime.datetime.now()
        base = datetime.datetime.combine(self.current_date, datetime.time(0,0))
        for key in ["Fajr","Dhuhr","Asr","Maghrib","Isha"]:
            t = day.get(key)
            if not t: continue
            try:
                h,m = map(int, t.split(":"))
            except:
                continue
            dt = base + datetime.timedelta(hours=h, minutes=m)
            if dt > now:
                return key, dt
        return None, None

    def update_next_prayer(self):
        key, dt = self.find_next_prayer()
        if key and dt:
            self.next_name.config(text=DISPLAY_NAMES.get(key,key))
            remaining = dt - datetime.datetime.now()
            total = int(remaining.total_seconds())
            if total < 0: total = 0
            h = total//3600
            m = (total%3600)//60
            s = total%60
            self.countdown.config(text=f"Ba9i: {h:02d}:{m:02d}:{s:02d}")
        else:
            self.next_name.config(text="--")
            self.countdown.config(text="")

    def tick(self):
        self.update_display()
        self.root.after(REFRESH_INTERVAL_MS, self.tick)

if __name__ == "__main__":
    root = tk.Tk()
    app = MosqueApp(root)
    root.mainloop()
