import os
import json
import psutil
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

# ஆட்டோமேஷன் மற்றும் மவுஸ் கண்ட்ரோல் லைப்ரரி பாதுகாப்பாக லோட் செய்ய
try:
    import pyautogui
    pyautogui.FAILSAFE = False
    gui_enabled = True
except Exception:
    pyautogui = None
    gui_enabled = False

app = FastAPI()
clients = set()
bot_task = None

# AI கேம் ஆட்டோமேஷன் (Space Bar அழுத்தும் கேம் பாட்)
async def ai_game_pilot(game_name):
    print(f"JARVIS: Auto-Pilot Engaged for {game_name}")
    try:
        while True:
            if gui_enabled:
                pyautogui.press('space')
            await asyncio.sleep(2)
    except asyncio.CancelledError:
        print("JARVIS: Auto-Pilot Disengaged.")

# எந்த லிங்கை ஓபன் செய்தாலும் Jarvis.html வரவழைக்க
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_jarvis_html(full_path: str):
    if os.path.exists("Jarvis.html"):
        with open("Jarvis.html", "r", encoding="utf-8") as f:
            return f.read()
    return "Jarvis.html file not found!"

# 24/7 WebSocket Bridge
@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    global bot_task
    await websocket.accept()
    clients.add(websocket)
    print("Boss Sarvesh, JARVIS Bridge Connected!")
    
    try:
        await websocket.send_text(json.dumps({"log": "JARVIS Ultimate Engine Online. Ready, Boss."}))
        
        # லைவ் CPU & RAM டேட்டாவை அனுப்ப
        async def send_telemetry():
            while True:
                try:
                    stats = {"stats": {"cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent}}
                    await websocket.send_text(json.dumps(stats))
                    await asyncio.sleep(2)
                except:
                    break

        telemetry_task = asyncio.create_task(send_telemetry())

        while True:
            data_text = await websocket.receive_text()
            data = json.loads(data_text)
            cmd_type = data.get("t")
            print(f"Command Received -> {cmd_type}")
            
            # 1. App Open & Close
            if cmd_type == "app_open":
                app_name = data.get("arg", "").lower()
                if os.name == 'nt': # Windows ஆக இருந்தால் ஆப் ஓபன் ஆகும்
                    if "youtube" in app_name:
                        os.system("start chrome https://www.youtube.com")
                    elif "notepad" in app_name:
                        os.system("start notepad")
                    else:
                        os.system(f"start {app_name}")
                await websocket.send_text(json.dumps({"log": f"Opened {app_name}"}))
                
            elif cmd_type == "app_close":
                app_name = data.get("arg")
                if os.name == 'nt':
                    os.system(f"taskkill /F /IM {app_name}.exe")
                await websocket.send_text(json.dumps({"log": f"Closed {app_name}"}))
                
            # 2. Volume & OS Controls
            elif cmd_type == "vol_up":
                if gui_enabled: pyautogui.press("volumeup", presses=3)
                await websocket.send_text(json.dumps({"log": "Volume Increased"}))
                
            elif cmd_type == "vol_down":
                if gui_enabled: pyautogui.press("volumedown", presses=3)
                await websocket.send_text(json.dumps({"log": "Volume Decreased"}))
                
            elif cmd_type == "mute":
                if gui_enabled: pyautogui.press("volumemute")
                await websocket.send_text(json.dumps({"log": "Audio Muted"}))
                
            # 3. Mouse Controls
            elif cmd_type == "mouse_move":
                x, y = data.get("x"), data.get("y")
                if gui_enabled and x and y:
                    pyautogui.moveTo(x, y)
                    
            elif cmd_type == "mouse_click":
                if gui_enabled: pyautogui.click()
                await websocket.send_text(json.dumps({"log": "Mouse Clicked"}))
                
            # 4. Game Automation
            elif cmd_type == "ai_game_start":
                game = data.get("game", "Game")
                if bot_task is None or bot_task.done():
                    bot_task = asyncio.create_task(ai_game_pilot(game))
                await websocket.send_text(json.dumps({"log": f"AI Auto-Pilot Active: {game}"}))
                
            elif cmd_type == "ai_game_stop":
                if bot_task and not bot_task.done():
                    bot_task.cancel()
                await websocket.send_text(json.dumps({"log": "AI Auto-Pilot Deactivated"}))

    except WebSocketDisconnect:
        print("UI Disconnected.")
    finally:
        clients.remove(websocket)
        try:
            telemetry_task.cancel()
        except:
            pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("backend:app", host="0.0.0.0", port=port)
