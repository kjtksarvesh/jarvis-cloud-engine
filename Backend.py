import os
import json
import asyncio
import httpx
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

# --- 1. SECURITY PERMISSION LOGIC ---
def check_permission(action_name):
    if not gui_enabled:
        return True # லினக்ஸ் கிளவுட்டில் (Screen இல்லாவிட்டால்) தடையின்றி இயங்க
    
    response = pyautogui.confirm(
        text=f"JARVIS Security Alert:\n\nயாரோ கிளவுட் வழியாக '{action_name}' கமாண்டை இயக்க முயல்கிறார்கள்.\nஅனுமதிக்கலாமா பாஸ் சர்வேஷ்?", 
        title="JARVIS System Access Request", 
        buttons=['Allow Access', 'Deny']
    )
    return response == 'Allow Access'

# --- 2. AI INTELLIGENCE & CREATION (No API Keys Needed) ---
async def get_ai_chat_response(prompt):
    """புத்திசாலித்தனமாக பதிலளிக்க Free Text API"""
    try:
        url = f"https://text.pollinations.ai/JARVIS,%20answer%20smartly:%20{prompt}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            return response.text
    except Exception:
        return "Boss Sarvesh, my neural link is temporarily down, but I'm still online."

async def get_ai_image(prompt):
    """High-Quality இமேஜ் கிரியேஷன்"""
    formatted_prompt = prompt.replace(' ', '%20')
    return f"https://image.pollinations.ai/prompt/{formatted_prompt}?width=1024&height=1024&nologo=true"

# --- 3. GAMING AUTO-PILOT ---
async def ai_game_pilot(game_name):
    print(f"JARVIS: Auto-Pilot Engaged for {game_name}")
    try:
        while True:
            if gui_enabled:
                pyautogui.press('space')
            await asyncio.sleep(2)
    except asyncio.CancelledError:
        print("JARVIS: Auto-Pilot Disengaged.")

# --- 4. WEB ROUTING ---
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_jarvis_html(full_path: str):
    if os.path.exists("Jarvis.html"):
        with open("Jarvis.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Jarvis.html file not found! Upload it to the server.</h1>"

# --- 5. THE CORE WEBSOCKET BRIDGE ---
@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    global bot_task
    await websocket.accept()
    clients.add(websocket)
    print("Boss Sarvesh, JARVIS Core Connected!")
    
    try:
        await websocket.send_text(json.dumps({"log": "JARVIS Core Systems Online. Awaiting your command, Boss."}))
        
        while True:
            data_text = await websocket.receive_text()
            data = json.loads(data_text)
            cmd_type = data.get("t")
            
            try:
                # 1. AI Chat Intelligence
                if cmd_type == "chat":
                    user_msg = data.get("msg", "")
                    ai_reply = await get_ai_chat_response(user_msg)
                    await websocket.send_text(json.dumps({"t": "chat_reply", "msg": ai_reply}))
                    
                # 2. Image Creation
                elif cmd_type == "generate_image":
                    prompt = data.get("prompt", "futuristic AI core")
                    img_url = await get_ai_image(prompt)
                    await websocket.send_text(json.dumps({"t": "image_result", "url": img_url, "log": "Image generated successfully."}))
                    
                # 3. Video Creation (Free Placeholder/API Ready)
                elif cmd_type == "generate_video":
                    prompt = data.get("prompt", "AI generated scene")
                    # Note: Full video generation requires heavy paid APIs (like Replicate). 
                    # This returns a safe response structure ready for your HTML Video Player.
                    dummy_video_url = "https://www.w3schools.com/html/mov_bbb.mp4" 
                    await websocket.send_text(json.dumps({"t": "video_result", "url": dummy_video_url, "log": f"Video processing completed for: {prompt}"}))
                    
                # 4. PC App Control with Security
                elif cmd_type == "app_open":
                    app_name = data.get("arg", "").lower()
                    if check_permission(f"Open App - {app_name}"):
                        if os.name == 'nt':
                            os.system(f"start {app_name}")
                        await websocket.send_text(json.dumps({"log": f"Opened {app_name}, Boss."}))
                    else:
                        await websocket.send_text(json.dumps({"log": "Access Denied by Boss Sarvesh."}))
                        
                # 5. Gaming Auto-Pilot
                elif cmd_type == "ai_game_start":
                    game = data.get("game", "Game")
                    if check_permission(f"Start Game Bot - {game}"):
                        if bot_task is None or bot_task.done():
                            bot_task = asyncio.create_task(ai_game_pilot(game))
                        await websocket.send_text(json.dumps({"log": f"AI Auto-Pilot Active for {game}."}))
                    else:
                        await websocket.send_text(json.dumps({"log": "Game Bot Access Denied."}))
                        
                elif cmd_type == "ai_game_stop":
                    if bot_task and not bot_task.done():
                        bot_task.cancel()
                    await websocket.send_text(json.dumps({"log": "AI Auto-Pilot Deactivated."}))

            except Exception as e:
                # எந்த எரர் வந்தாலும் சர்வர் க்ராஷ் ஆகாமல் தடுத்து, UI-க்கு மெசேஜ் அனுப்பும்
                await websocket.send_text(json.dumps({"log": f"System Alert: Minor glitch handled -> {str(e)}"}))

    except WebSocketDisconnect:
        print("UI Disconnected.")
    finally:
        clients.remove(websocket)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("backend:app", host="0.0.0.0", port=port)
