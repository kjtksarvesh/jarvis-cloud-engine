import asyncio
import websockets
import json
import psutil
import os
import http.server
import socketserver
import threading
import webbrowser

PORT_HTTP = 8080
PORT_WS = 8765
clients = set()

# 1. HTML கோப்பை லோக்கல் சர்வரில் சர்வ் செய்ய (Serve Jarvis.html)
class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # டெர்மினலில் தேவையற்ற HTTP லாப்ஸைத் தவிர்க்க
        pass

def start_http_server():
    with socketserver.TCPServer(("", PORT_HTTP), Handler) as httpd:
        print(f"🌐 Jarvis UI Server running at: http://localhost:{PORT_HTTP}/Jarvis.html")
        httpd.serve_forever()

# 2. CPU & RAM டெலிமெட்ரி டேட்டாவை அனுப்ப
async def send_telemetry():
    while True:
        if clients:
            stats = {
                "stats": {
                    "cpu": psutil.cpu_percent(),
                    "ram": psutil.virtual_memory().percent
                }
            }
            message = json.dumps(stats)
            for client in clients:
                try:
                    await client.send(message)
                except:
                    pass
        await asyncio.sleep(2)

# 3. HTML-ல் இருந்து வரும் கமாண்ட்களை ஹேண்டில் செய்ய (WebSocket Bridge)
async def handle_commands(websocket):
    clients.add(websocket)
    print("Boss Sarvesh, UI Bridge Connected!")
    await websocket.send(json.dumps({"log": "System Bridge Online, Boss Sarvesh. JARVIS is ready."}))
    
    try:
        async for message in websocket:
            data = json.loads(message)
            cmd_type = data.get("t")
            
            if cmd_type == "app_open":
                app_name = data.get("arg")
                print(f"JARVIS: Opening application -> {app_name}")
                os.system(f"start {app_name}")
                await websocket.send(json.dumps({"log": f"Opened {app_name}"}))
                
            elif cmd_type == "app_close":
                app_name = data.get("arg")
                print(f"JARVIS: Closing application -> {app_name}")
                os.system(f"taskkill /F /IM {app_name}.exe")
                await websocket.send(json.dumps({"log": f"Closed {app_name}"}))
                
    except websockets.exceptions.ConnectionClosed:
        print("UI Disconnected.")
    finally:
        clients.remove(websocket)

async def main():
    # HTTP சர்வரை ஒரு தனி Thread-ல் இயக்க (Background-ல் இயங்க)
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()
    
    # பிரவுசரில் ஆட்டோமேட்டிக்காக Jarvis.html-ஐ திறக்க
    webbrowser.open(f"http://localhost:{PORT_HTTP}/Jarvis.html")

    # WebSocket Telemetry Task-ஐ ஸ்டார்ட் செய்ய
    asyncio.create_task(send_telemetry())
    
    # WebSocket சர்வரை 8765 போர்ட்டில் ரன் செய்ய
    async with websockets.serve(handle_commands, "127.0.0.1", PORT_WS):
        print(f"🚀 JARVIS WebSocket Bridge Running on ws://127.0.0.1:{PORT_WS}")
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nJARVIS System Shutting Down...")
