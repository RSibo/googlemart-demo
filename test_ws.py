import asyncio
import websockets
import json
import os

async def test_bidi():
    token = os.popen("gcloud auth print-access-token").read().strip()
    project = "cloud-llm-preview1"
    location = "us-central1"
    model_id = "gemini-3.1-flash-live-preview-04-2026"
    host = f"{location}-autopush-aiplatform.sandbox.googleapis.com"
    uri = f"wss://{host}/ws/google.cloud.aiplatform.v1beta1.LlmBidiService/BidiGenerateContent"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    try:
        async with websockets.connect(uri, additional_headers=headers) as ws:
            setup_msg = {
                "setup": {
                    "model": f"projects/{project}/locations/{location}/publishers/google/models/{model_id}",
                    "generationConfig": {
                        "responseModalities": ["VIDEO"],
                        "speechConfig": {
                            "voiceConfig": {
                                "prebuiltVoiceConfig": {"voiceName": "Puck"}
                            },
                            "languageCode": "en-US"
                        }
                    },
                    "avatarConfig": {"avatar_name": "Ben"},
                    "inputAudioTranscription": {"model": "RNNT"},
                    "outputAudioTranscription": {"model": "RNNT"}
                }
            }
            print("Sending setup...")
            await ws.send(json.dumps(setup_msg))
            resp = await ws.recv()
            print("Setup response:", resp)
            
            greeting_msg = {
                "clientContent": {
                    "turns": [
                        {
                            "role": "user",
                            "parts": [{"text": "Hello"}]
                        }
                    ],
                    "turnComplete": True
                }
            }
            print("Sending greeting...")
            await ws.send(json.dumps(greeting_msg))
            
            for _ in range(5):
                resp = await ws.recv()
                print("Response:", resp[:200])
                
    except Exception as e:
        print("Error:", e)

asyncio.run(test_bidi())
