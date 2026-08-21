import asyncio
import websockets
import os

PORT = int(os.environ.get("PORT", 9999))

clients = {}   # name -> websocket
sender_ws = None

async def notify_sender(msg):
    global sender_ws
    if sender_ws:
        try:
            await sender_ws.send(msg)
        except Exception:
            sender_ws = None

async def handle_client(websocket):
    global sender_ws
    name = None
    try:
        name = await websocket.recv()
        if not name:
            return

        if name == "__SENDER__":
            sender_ws = websocket
            print("[+] Sender GUI connected")
            for n in list(clients.keys()):
                try:
                    await websocket.send(f"__JOIN__:{n}")
                except Exception:
                    pass
            async for message in websocket:
                try:
                    # Supports: "TARGET||TEXT:message", "TARGET||IMAGE:base64data", "TARGET||UPDATE:base64data"
                    if "||" in message:
                        target, payload = message.split("||", 1)
                        targets = list(clients.items()) if target == "Everyone" else [(target, clients[target])] if target in clients else []
                        for n, ws in targets:
                            try:
                                await ws.send(payload)
                            except Exception:
                                pass
                except Exception as e:
                    print(f"[!] Error processing sender message: {e}")
            return

        clients[name] = websocket
        print(f"[+] {name} connected")
        await notify_sender(f"__JOIN__:{name}")

        async for _ in websocket:
            pass

    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        print(f"[!] Error with client {name}: {e}")
    finally:
        if name and name != "__SENDER__":
            if name in clients:
                del clients[name]
                print(f"[-] {name} disconnected")
                await notify_sender(f"__LEAVE__:{name}")
        if websocket == sender_ws:
            sender_ws = None
            print("[-] Sender GUI disconnected")

async def main():
    print(f"WebSocket server starting on port {PORT}...")
    async with websockets.serve(handle_client, "0.0.0.0", PORT, max_size=100 * 1024 * 1024):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
