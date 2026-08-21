import asyncio
import websockets
import threading
import tkinter as tk
from tkinter import scrolledtext, filedialog
import datetime
import base64

SERVER_URL = "wss://laila-leavenless-overinsistently.ngrok-free.dev"  # <-- Replace with your ngrok URL

clients_online = []
ws_connection = None
loop = None

def get_time():
    return datetime.datetime.now().strftime("%H:%M:%S")

def log(widget, msg):
    try:
        widget.insert(tk.END, f"[{get_time()}] {msg}\n")
        widget.see(tk.END)
    except Exception:
        pass

async def connect_as_sender(log_widget, client_listbox):
    global ws_connection
    while True:
        try:
            async with websockets.connect(SERVER_URL, max_size=100*1024*1024) as ws:
                ws_connection = ws
                await ws.send("__SENDER__")
                log(log_widget, "✅ Connected to server as sender")
                async for message in ws:
                    if message.startswith("__JOIN__:"):
                        name = message.split(":", 1)[1]
                        if name not in clients_online:
                            clients_online.append(name)
                            client_listbox.insert(tk.END, name)
                            log(log_widget, f"👤 {name} connected")
                    elif message.startswith("__LEAVE__:"):
                        name = message.split(":", 1)[1]
                        if name in clients_online:
                            clients_online.remove(name)
                            items = client_listbox.get(0, tk.END)
                            for i, item in enumerate(items):
                                if item == name:
                                    client_listbox.delete(i)
                                    break
                            log(log_widget, f"👋 {name} disconnected")
        except Exception:
            ws_connection = None
            log(log_widget, "⚠️ Disconnected. Reconnecting in 5s...")
            await asyncio.sleep(5)

def run_loop(log_widget, client_listbox):
    global loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(connect_as_sender(log_widget, client_listbox))

def send_message(payload, target, log_widget, label):
    global ws_connection, loop
    if not ws_connection:
        log(log_widget, "❌ Not connected!")
        return
    full = f"{target}||{payload}"
    asyncio.run_coroutine_threadsafe(ws_connection.send(full), loop)
    log(log_widget, f"📨 Sent {label} to {target}")

def send_text(msg_entry, target_var, log_widget):
    msg = msg_entry.get("1.0", tk.END).strip()
    if not msg:
        return
    send_message(f"TEXT:{msg}", target_var.get(), log_widget, f"\"{msg[:30]}{'...' if len(msg)>30 else ''}\"")
    msg_entry.delete("1.0", tk.END)

def send_image(target_var, log_widget):
    path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")])
    if not path:
        return
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    send_message(f"IMAGE:{data}", target_var.get(), log_widget, "image")

def send_update(target_var, log_widget):
    path = filedialog.askopenfilename(filetypes=[("Executable", "*.exe")])
    if not path:
        return
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    send_message(f"UPDATE:{data}", target_var.get(), log_widget, "client update")

def update_target_menu(client_listbox, target_var, target_menu):
    names = list(client_listbox.get(0, tk.END))
    menu = target_menu["menu"]
    menu.delete(0, "end")
    menu.add_command(label="Everyone", command=lambda: target_var.set("Everyone"))
    for name in names:
        menu.add_command(label=name, command=lambda n=name: target_var.set(n))

def main():
    root = tk.Tk()
    root.title("📡 PopupSender")
    root.geometry("600x560")
    root.configure(bg="#0f0f1a")

    header = tk.Frame(root, bg="#1a1a2e", pady=10)
    header.pack(fill=tk.X)
    tk.Label(header, text="📡 POPUP SENDER", font=("Courier New", 18, "bold"),
             fg="#00ffcc", bg="#1a1a2e").pack()
    tk.Label(header, text="WebSocket mode  •  Text / Image / Update",
             font=("Courier New", 9), fg="#666699", bg="#1a1a2e").pack()

    main_frame = tk.Frame(root, bg="#0f0f1a")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

    # Left: friends list
    left = tk.Frame(main_frame, bg="#0f0f1a", width=160)
    left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
    left.pack_propagate(False)
    tk.Label(left, text="ONLINE FRIENDS", font=("Courier New", 9, "bold"),
             fg="#00ffcc", bg="#0f0f1a").pack(anchor="w")
    client_listbox = tk.Listbox(left, bg="#1a1a2e", fg="#e0e0ff",
                                 font=("Courier New", 10), selectbackground="#00ffcc",
                                 selectforeground="#0f0f1a", bd=0, highlightthickness=1,
                                 highlightcolor="#00ffcc")
    client_listbox.pack(fill=tk.BOTH, expand=True, pady=4)

    # Right
    right = tk.Frame(main_frame, bg="#0f0f1a")
    right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    tk.Label(right, text="MESSAGE", font=("Courier New", 9, "bold"),
             fg="#00ffcc", bg="#0f0f1a").pack(anchor="w")
    msg_entry = scrolledtext.ScrolledText(right, height=5, bg="#1a1a2e", fg="#ffffff",
                                           font=("Courier New", 11), insertbackground="#00ffcc",
                                           bd=0, highlightthickness=1, highlightcolor="#00ffcc",
                                           wrap=tk.WORD)
    msg_entry.pack(fill=tk.X, pady=(4, 8))

    # Target row
    controls = tk.Frame(right, bg="#0f0f1a")
    controls.pack(fill=tk.X)
    tk.Label(controls, text="To:", font=("Courier New", 10), fg="#aaaacc", bg="#0f0f1a").pack(side=tk.LEFT)
    target_var = tk.StringVar(value="Everyone")
    target_menu = tk.OptionMenu(controls, target_var, "Everyone")
    target_menu.config(bg="#1a1a2e", fg="#e0e0ff", font=("Courier New", 10),
                       activebackground="#00ffcc", activeforeground="#0f0f1a",
                       highlightthickness=0, bd=0)
    target_menu["menu"].config(bg="#1a1a2e", fg="#e0e0ff", font=("Courier New", 10))
    target_menu.pack(side=tk.LEFT, padx=8)
    tk.Button(controls, text="↻", font=("Courier New", 9),
              bg="#1a1a2e", fg="#aaaacc", bd=0, padx=6, pady=4,
              command=lambda: update_target_menu(client_listbox, target_var, target_menu)
              ).pack(side=tk.LEFT)
    tk.Button(controls, text="SEND TEXT ▶",
              font=("Courier New", 10, "bold"),
              bg="#00ffcc", fg="#0f0f1a", activebackground="#00ccaa",
              bd=0, padx=12, pady=6,
              command=lambda: send_text(msg_entry, target_var, log_widget)
              ).pack(side=tk.RIGHT)

    msg_entry.bind("<Control-Return>", lambda e: send_text(msg_entry, target_var, log_widget))

    # Image + Update buttons
    extra = tk.Frame(right, bg="#0f0f1a")
    extra.pack(fill=tk.X, pady=(8, 0))
    tk.Button(extra, text="🖼 SEND IMAGE",
              font=("Courier New", 10, "bold"),
              bg="#1a3a5c", fg="#00b4d8", activebackground="#1a4a7c",
              bd=0, padx=12, pady=6,
              command=lambda: send_image(target_var, log_widget)
              ).pack(side=tk.LEFT, padx=(0, 8))
    tk.Button(extra, text="⬆ PUSH UPDATE",
              font=("Courier New", 10, "bold"),
              bg="#3a1a1a", fg="#ff6666", activebackground="#5a2a2a",
              bd=0, padx=12, pady=6,
              command=lambda: send_update(target_var, log_widget)
              ).pack(side=tk.LEFT)

    # Log
    tk.Label(right, text="LOG", font=("Courier New", 9, "bold"),
             fg="#00ffcc", bg="#0f0f1a").pack(anchor="w", pady=(12, 0))
    log_widget = scrolledtext.ScrolledText(right, height=8, bg="#0a0a14", fg="#7777aa",
                                            font=("Courier New", 9), bd=0,
                                            highlightthickness=1, highlightcolor="#333355",
                                            wrap=tk.WORD)
    log_widget.pack(fill=tk.BOTH, expand=True, pady=4)
    log(log_widget, "🚀 Connecting to server...")

    t = threading.Thread(target=run_loop, args=(log_widget, client_listbox), daemon=True)
    t.start()

    root.mainloop()

if __name__ == "__main__":
    main()
