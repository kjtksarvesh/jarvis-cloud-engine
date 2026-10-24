import os
import json
import psutil
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

# கம்ப்யூட்டர் மவுஸ்/கீபோர்டு கண்ட்ரோலுக்கான லைப்ரரி (Render-ல் எரர் வராமல் தடுக்க Try/Except)
try:
    import pyautogui
    pyautogui.FAILSAFE = False
except ImportError:
    pyautogui = None

app = FastAPI()
clients = set()
bot_task = None

# AI Game Automation லூப் (உதா: Mario Bot)
async def ai_game_pilot(game_name):
    print(f"JARVIS: Starting AI Game Pilot for {game_name}")
    try:
        while True:
            if pyautogui:
                pyautogui.press('space') # கேமில் குதிக்க (Jump)
            await asyncio.sleep(2)
    except asyncio.CancelledError:
        print("JARVIS: AI Game Pilot Stopped.")

@app.get("/", response_class=HTMLResponse)
async def home():
    if os.path.exists("Jarvis.html"):
        with open("Jarvis.html", "r", encoding="utf-8") as f:
            return f.read()
    return "Jarvis.html file not found!"

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    global bot_task
    await websocket.accept()
    clients.add(websocket)
    print("Boss Sarvesh, UI WebSocket Connected!")
    
    try:
        await websocket.send_text(json.dumps({"log": "System Bridge Online, Boss Sarvesh. JARVIS is ready."}))
        
        async def send_stats():
            while True:
                try:
                    stats = {"stats": {"cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent}}
                    await websocket.send_text(json.dumps(stats))
                    await asyncio.sleep(2)
                except:
                    break

        stats_task = asyncio.create_task(send_stats())

        while True:
            data_text = await websocket.receive_text()
            data = json.loads(data_text)
            cmd_type = data.get("t")
            
            # --- 1. App Open / Close ---
            if cmd_type == "app_open":
                app_name = data.get("arg")
                if os.name == 'nt':
                    os.system(f"start {app_name}")
                await websocket.send_text(json.dumps({"log": f"Opened {app_name}"}))
                
            elif cmd_type == "app_close":
                app_name = data.get("arg")
                if os.name == 'nt':
                    os.system(f"taskkill /F /IM {app_name}.exe")
                await websocket.send_text(json.dumps({"log": f"Closed {app_name}"}))
            
            # --- 2. OS Media Controls ---
            elif cmd_type == "vol_up":
                if pyautogui: pyautogui.press("volumeup", presses=3)
                await websocket.send_text(json.dumps({"log": "Volume Increased"}))
                
            elif cmd_type == "vol_down":
                if pyautogui: pyautogui.press("volumedown", presses=3)
                await websocket.send_text(json.dumps({"log": "Volume Decreased"}))
                
            elif cmd_type == "mute":
                if pyautogui: pyautogui.press("volumemute")
                await websocket.send_text(json.dumps({"log": "Audio Muted/Unmuted"}))
            
            # --- 3. Hand Gesture & Mouse Control ---
            elif cmd_type == "mouse_move":
                x, y = data.get("x"), data.get("y")
                if pyautogui and x and y:
                    pyautogui.moveTo(x, y)
                    
            elif cmd_type == "mouse_click":
                if pyautogui: pyautogui.click()
                await websocket.send_text(json.dumps({"log": "Mouse Clicked via Gesture"}))
                
            # --- 4. Game Automation (AI Pilot) ---
            elif cmd_type == "ai_game_start":
                game = data.get("game")
                if bot_task is None or bot_task.done():
                    bot_task = asyncio.create_task(ai_game_pilot(game))
                await websocket.send_text(json.dumps({"log": f"AI Game Pilot Active: {game}"}))
                
            elif cmd_type == "ai_game_stop":
                if bot_task and not bot_task.done():
                    bot_task.cancel()
                await websocket.send_text(json.dumps({"log": "AI Game Pilot Deactivated"}))

    except WebSocketDisconnect:
        print("UI Disconnected.")
    finally:
        clients.remove(websocket)
        try:
            stats_task.cancel()
        except:
            pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    uvicorn.run("backend:app", host="0.0.0.0", port=port)
