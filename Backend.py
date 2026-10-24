import platform
import threading
import time
import urllib.parse
import webbrowser
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Cloud-ல் Error வராமல் தடுக்க Try-Except பிளாக்
try:
    import pywhatkit
    import pyautogui
    import pyttsx3
    DESKTOP_ENV = True
except ImportError:
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
        current_os = platform.system()
        if current_os == "Windows":
            self.engine.setProperty('voice', voices[0].id)
        self.engine.setProperty('rate', 170)

    def speak(self, text):
        print(f"{self.ai_name}: {text}")
        if DESKTOP_ENV:
            self.engine.say(text)
            self.engine.runAndWait()

    def play_super_mario(self):
        self.speak(f"Opening Super Mario Bros for you, {self.user_name}.")
        webbrowser.open("https://supermario-game.com/")
        if DESKTOP_ENV:
            time.sleep(5)
            screen_w, screen_h = pyautogui.size()
            pyautogui.click(screen_w // 2, screen_h // 2)
            pyautogui.press("enter")

    def handle_youtube(self, query):
        if "play" in query:
            song = query.replace("play", "").replace("on youtube", "").replace("youtube", "").strip()
            self.speak(f"Playing {song} on YouTube")
            if DESKTOP_ENV:
                pywhatkit.playonyt(song)
        elif "search" in query:
            search_term = query.replace("search", "").replace("youtube", "").strip()
            self.speak(f"Searching for {search_term}")
            webbrowser.open(f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(search_term)}")
        elif DESKTOP_ENV and ("pause" in query or "play video" in query):
            pyautogui.press("k")
        elif DESKTOP_ENV and "full screen" in query:
            pyautogui.press("f")

    def process_command(self, query):
        query = query.lower()
        if "mario" in query:
            self.play_super_mario()
        elif "youtube" in query or "play" in query:
            self.handle_youtube(query)
        else:
            self.speak(f"Command received: {query}")

app = FastAPI()
jarvis = JarvisBackend()

class Command(BaseModel):
    query: str

@app.post("/api/command")
def receive_command(command: Command, background_tasks: BackgroundTasks):
    background_tasks.add_task(jarvis.process_command, command.query)
    return {"status": "success", "message": f"JARVIS is executing: {command.query}"}

@app.get("/", response_class=HTMLResponse)
def web_interface():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>JARVIS Control Panel</title>
        <style>
            body { font-family: sans-serif; background: #121212; color: #00ffcc; text-align: center; padding: 20px; }
            input { width: 80%; padding: 15px; margin: 20px 0; border-radius: 8px; border: 1px solid #00ffcc; background: #222; color: white; font-size: 16px; }
            button { padding: 15px 30px; background: #00ffcc; color: #121212; border: none; border-radius: 8px; font-size: 18px; font-weight: bold; cursor: pointer; }
        </style>
    </head>
    <body>
        <h2>JARVIS Web Interface</h2>
        <input type="text" id="query" placeholder="Type command here..." onkeydown="if(event.key === 'Enter') sendCommand()">
        <br>
        <button onclick="sendCommand()">Send to JARVIS</button>
        <p id="status"></p>

        <script>
            function sendCommand() {
                const query = document.getElementById('query').value;
                document.getElementById('status').innerText = "Sending command...";
                fetch('/api/command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status').innerText = data.message;
                    document.getElementById('query').value = '';
                });
            }
        </script>
    </body>
    </html>
    """
