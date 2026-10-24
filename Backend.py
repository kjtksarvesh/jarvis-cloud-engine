import platform
import threading
import time
import urllib.parse
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Safely handle imports on headless servers like Render
try:
    import webbrowser
    import pywhatkit
    import pyautogui
    import pyttsx3
    DESKTOP_ENV = True
except Exception:
    DESKTOP_ENV = False

class JarvisBackend:
    def __init__(self, user_name="Sarvesh", ai_name="JARVIS"):
        self.user_name = user_name
        self.ai_name = ai_name
        if DESKTOP_ENV:
            self.engine = pyttsx3.init()
            self.configure_voice()

    def configure_voice(self):
        voices = self.engine.getProperty('voices')
        if platform.system() == "Windows":
            self.engine.setProperty('voice', voices[0].id)
        self.engine.setProperty('rate', 170)

    def speak(self, text):
        print(f"{self.ai_name}: {text}")
        if DESKTOP_ENV:
            self.engine.say(text)
            self.engine.runAndWait()

    def process_command(self, query):
        query = query.lower()
        if "mario" in query:
            self.speak("Opening Super Mario.")
            if DESKTOP_ENV:
                webbrowser.open("https://supermario-game.com/")
                time.sleep(5)
                screen_w, screen_h = pyautogui.size()
                pyautogui.click(screen_w // 2, screen_h // 2)
                pyautogui.press("enter")
        elif "youtube" in query or "play" in query:
            self.speak("Processing YouTube command.")
            if DESKTOP_ENV:
                if "play" in query:
                    song = query.replace("play", "").replace("youtube", "").strip()
                    pywhatkit.playonyt(song)
        else:
            self.speak(f"Received: {query}")

app = FastAPI()
jarvis = JarvisBackend()

class Command(BaseModel):
    query: str

@app.post("/api/command")
def receive_command(command: Command, background_tasks: BackgroundTasks):
    background_tasks.add_task(jarvis.process_command, command.query)
    return {"status": "success", "message": f"Executing: {command.query}"}

@app.get("/", response_class=HTMLResponse)
def web_interface():
    return """
    <!DOCTYPE html>
    <html>
    <head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>JARVIS</title></head>
    <body style="background:#121212; color:#0ff; text-align:center; font-family:sans-serif; padding:20px;">
        <h2>JARVIS Online</h2>
        <input type="text" id="query" placeholder="Enter command" style="padding:10px; width:80%;">
        <button onclick="sendCommand()" style="padding:10px; margin-top:10px;">Send</button>
        <p id="status"></p>
        <script>
            function sendCommand() {
                const query = document.getElementById('query').value;
                document.getElementById('status').innerText = "Sending...";
                fetch('/api/command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                }).then(res => res.json()).then(data => {
                    document.getElementById('status').innerText = data.message;
                });
            }
        </script>
    </body>
    </html>
    """
