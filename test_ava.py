import asyncio
import websockets
import json

TOKEN = open("/tmp/gemini_token.txt").read().strip()

async def test_ava():
    uri = "wss://us-central1-autopush-aiplatform.sandbox.googleapis.com/ws/google.cloud.aiplatform.v1.LlmBidiService/BidiGenerateContent"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        async with websockets.connect(uri, additional_headers=headers) as ws:
            setup = {
                "setup": {
                    "model": "projects/cloud-llm-preview1/locations/us-central1/publishers/google/models/gemini_live_rev25_ava",
                    "avatarConfig": {
                        "avatar_name": "Ben"
                    },
                    "generationConfig": {
                        "responseModalities": ["AUDIO"],
                        "speechConfig": {
                            "voiceConfig": {
                                "prebuiltVoiceConfig": {"voiceName": "Puck"}
                            },
                            "languageCode": "en-US"
                        }
                    }
                }
            }
            
            print("Connected, sending setup...")
            await ws.send(json.dumps(setup))
            resp = await ws.recv()
            print("Setup response:", resp[:200])
            
            greeting_msg = {
                "clientContent": {
                    "turns": [
                        {
                            "role": "user",
                            "parts": [{"text": "Hello, I have just connected."}]
                        }
                    ],
                    "turnComplete": True
                }
            }
            print("Sending clientContent greeting...")
            await ws.send(json.dumps(greeting_msg))
            
            for _ in range(5):
                resp = await ws.recv()
                print("Greeting response:", resp[:200])
                
    except Exception as e:
        print("Error:", e)

asyncio.run(test_ava())
