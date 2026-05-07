import asyncio
import websockets
import json

async def test_local():
    uri = "ws://localhost:8000/ws"
    try:
        async with websockets.connect(uri) as ws:
            setup = {
                "type": "setup",
                "content": {
                    "accessToken": open("/tmp/gemini_token.txt").read().strip(),
                    "projectId": "cloud-llm-preview1",
                    "location": "us-central1",
                    "modelId": "gemini-3.1-flash-live-preview-04-2026",
                    "voice": "Puck",
                    "avatar": "Ben"
                }
            }
            await ws.send(json.dumps(setup))
            
            resp = await asyncio.wait_for(ws.recv(), timeout=2.0)
            print("Received:", resp[:200])
                
    except Exception as e:
        print("Error:", e)

asyncio.run(test_local())
