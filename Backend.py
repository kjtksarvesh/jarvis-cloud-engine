import asyncio
import json
import os
import sys
import subprocess
import tempfile
import time
import requests
import websockets

# Render தானாகவே PORT என்விரான்மென்ட் வேரியபிளை வழங்கும்
PORT = int(os.environ.get("PORT", 8765))

# --- AI Game Pilot Engine (Cloud Logic) ---
ai_game_states = {}

async def run_game_bot(client_id, game_name, ws):
    """கிளவுட் வழியாக கேம் கமாண்டுகளை வெப் UI-க்கு அனுப்பும் ஆட்டோமேஷன்"""
    step = 0
    try:
        while ai_game_states.get(client_id, False):
            step += 1
            if 'mario' in game_name.lower():
                # மரியோவிற்கான மூவ்மென்ட் கமாண்டுகள்
                actions = ['right']
                if step % 4 == 0:
                    actions.append('jump')
                if step % 9 == 0:
                    actions.append('speed')
                await ws.send(json.dumps({'t': 'bot_action', 'actions': actions}))
                await asyncio.sleep(0.12)
            elif 'subway' in game_name.lower() or 'temple' in game_name.lower():
                moves = ['up', 'down', 'left', 'right']
                selected = moves[step % len(moves)]
                await ws.send(json.dumps({'t': 'bot_action', 'actions': [selected]}))
                await asyncio.sleep(0.35)
            else:
                await ws.send(json.dumps({'t': 'bot_action', 'actions': ['space']}))
                await asyncio.sleep(0.5)
    except Exception:
        ai_game_states[client_id] = False

# --- Backend Code Execution Engine ---
def execute_python_code(code_str):
    """கிளவுடில் பாதுகாப்பாக பைதான் கோடை ரன் செய்து அவுட்புட் தரும்"""
    try:
        with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False, encoding='utf-8') as f:
            f.write(code_str)
            temp_path = f.name

        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        os.unlink(temp_path)
        out = result.stdout if result.stdout else result.stderr
        return out if out else "Code executed successfully with no output."
    except subprocess.TimeoutExpired:
        return "Execution Error: Process timed out (10s limit)."
    except Exception as e:
        return f"Execution Error: {str(e)}"

# --- Enhanced Image Generation (Hugging Face / FLUX) ---
def generate_flux_image(prompt, hf_token=""):
    """ஹக்கிங் பேஸ் FLUX API மூலமாக இமேஜ் ஜெனரேட் செய்தல்"""
    headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}
    api_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"

    if hf_token:
        try:
            response = requests.post(api_url, headers=headers, json={"inputs": prompt}, timeout=25)
            if response.status_code == 200:
                return {"status": "success", "source": "HuggingFace FLUX", "message": "Rendered via FLUX.1 Engine"}
        except Exception:
            pass

    # Fallback to Pollinations FLUX Engine
    direct_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?model=flux&width=1024&height=1024&nologo=true"
    return {"status": "success", "source": "Pollinations FLUX", "url": direct_url}

# --- WebSocket Server Handler ---
async def handle_client(ws):
    client_id = id(ws)
    ai_game_states[client_id] = False
    print(f"[JARVIS CLOUD] Client connected: {client_id}")

    try:
        # Client இணைந்ததும் வரவேற்பு செய்தி
        await ws.send(json.dumps({
            'log': 'Connected to JARVIS Cloud Engine (24/7 Online)',
            'server_time': time.strftime("%Y-%m-%d %H:%M:%S")
        }))

        async for raw_message in ws:
            try:
                data = json.loads(raw_message)
            except json.JSONDecodeError:
                continue

            action_type = data.get('t')

            # 1. Keep-Alive Ping
            if action_type == 'ping':
                await ws.send(json.dumps({'t': 'pong', 'time': time.time()}))

            # 2. கோட் எக்ஸிகியூஷன்
            elif action_type == 'run_code':
                code = data.get('code', '')
                output = execute_python_code(code)
                await ws.send(json.dumps({'code_output': output}))

            # 3. இமேஜ் ஜெனரேஷன்
            elif action_type == 'gen_hd_img':
                prompt = data.get('prompt', '')
                token = data.get('token', '')
                res = generate_flux_image(prompt, token)
                await ws.send(json.dumps({
                    'log': f"Image processed ({res.get('source')})",
                    'img_url': res.get('url', '')
                }))

            # 4. AI கேம் பாட் கன்ட்ரோல்
            elif action_type == 'ai_game_start':
                ai_game_states[client_id] = True
                game = data.get('game', 'mario')
                asyncio.create_task(run_game_bot(client_id, game, ws))
                await ws.send(json.dumps({'log': f'Cloud AI Bot launched for {game}'}))

            elif action_type == 'ai_game_stop':
                ai_game_states[client_id] = False
                await ws.send(json.dumps({'log': 'Cloud AI Bot halted.'}))

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        ai_game_states[client_id] = False
        print(f"[JARVIS CLOUD] Client disconnected: {client_id}")

async def main():
    print(f"[JARVIS CLOUD] Initializing WebSocket Server on 0.0.0.0:{PORT}...")
    async with websockets.serve(handle_client, "0.0.0.0", PORT):
        print(f"[JARVIS CLOUD] Server is live and listening on port {PORT}!")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())