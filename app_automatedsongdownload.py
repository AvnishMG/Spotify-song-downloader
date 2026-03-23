import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import threading
import sys
import os
import csv
import subprocess
import time
import webbrowser
from pathlib import Path

def resource_path(filename):
    """Get absolute path to resource, works for dev and PyInstaller."""
    if getattr(sys, 'frozen', False):  # running as exe
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.abspath("."), filename)

def get_yt_dlp_path():
    if getattr(sys, 'frozen', False):  # running as exe
        return os.path.join(sys._MEIPASS, "yt-dlp.exe")
    return "yt-dlp.exe"  # running normally

yt_dlp_path = get_yt_dlp_path()

root = tk.Tk()
root.title("Spotify Downloader")
root.iconbitmap(resource_path("songdownload.ico"))

tk.Label(root, text="Playlist Name:").pack()
name_entry = tk.Entry(root, width=50)
name_entry.pack()

log_area = scrolledtext.ScrolledText(root, width=60, height=20)
log_area.pack()

def log(text):
    log_area.insert(tk.END, text + "\n")
    log_area.see(tk.END)
    log_area.update_idletasks()

progress = ttk.Progressbar(root, length=400, mode='determinate')
progress.pack(pady=5)

# 👉 BUTTONS
done_button = tk.Button(root, text="Done", state=tk.DISABLED, command=root.destroy)
done_button.pack(side=tk.RIGHT, padx=10, pady=10)
done_button.config(text="Bro cooked🍲")  # 👈 changes button text

abort_button = tk.Button(root, text="Abort", command=root.destroy)
abort_button.pack(side=tk.RIGHT, padx=10, pady=10)

def start_download():

    playlist_name = name_entry.get()

    # 🌐 Open exportify
    log("Opening Exportify...")
    webbrowser.open("https://exportify.net/")
    time.sleep(3)
    messagebox.showinfo("Export CSV", "Click 'Export' button next to the playlist u want then press OK\n(If not logged into Exportify...Do that.\nthen select playlist and press OK)")
    
    # 📂 STEP 2: Find latest CSV in Downloads
    downloads = Path.home() / "Downloads"
    csv_files = list(downloads.glob("*.csv"))
    latest_csv = max(csv_files, key=os.path.getctime)

    log(f"Using CSV: {latest_csv}")

    with open(latest_csv, newline='', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
        total_tracks = len(reader)
        progress['maximum'] = total_tracks

    # 📁 STEP 3: Create folders
    messagebox.showinfo("Cooking...", "aight lemme cook🥀")

    desktop = Path.home()
    if (desktop / "OneDrive" / "Desktop").exists():
        desktop = desktop / "OneDrive" / "Desktop"
    else:
        desktop = desktop / "Desktop"

    playlist_name = name_entry.get()
    playlist_folder = desktop / playlist_name
    playlist_folder.mkdir(exist_ok=True)

    log(f"Created folder: {playlist_folder}")

    # 📥 STEP 4: Download songs
    output_template = str(playlist_folder / "%(title)s.%(ext)s")

    with open(latest_csv, newline='', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))  # make it a list so we can count and enumerate
        total_tracks = len(reader)
        progress['maximum'] = total_tracks  # set the max value of the progress bar

        
        for i, row in enumerate(reader, start=1):# ... your yt-dlp download code ...
            artist = row.get("Artist Name(s)", "")
            track = row.get("Track Name", "")

            if artist and track:
                query = f"{artist} - {track}"
                log(f"Downloading: {query}")

                subprocess.run([
                    yt_dlp_path,
                    "-x",
                    "--audio-format", "mp3",
                    "--audio-quality", "0",
                    "--ignore-errors",
                    "-o", output_template,
                    f"ytsearch:{query}"
                ], 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW)

                time.sleep(1)
    
                progress['value'] = i  # update the bar
                root.update_idletasks()  # redraw bar
    # ❌📥 STEP 5: Delete CSV after downloads
    try:
        os.remove(latest_csv)
        log(f"Deleted CSV: {latest_csv}")
    except Exception as e:
        log(f"Could not delete CSV: {e}")

    done_button.config(state=tk.NORMAL)  # now user can click Done
    log("Downloads finished👍 Admit i cooked to close.\nits in ur desktop")

start_button = tk.Button(root, text="Start Download",
                         command=lambda: threading.Thread(target=start_download, daemon=True).start())
start_button.pack(pady=10)

root.mainloop()