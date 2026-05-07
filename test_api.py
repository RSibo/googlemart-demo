import asyncio
import websockets
import json
import sys

TOKEN = "YOUR_TOKEN_HERE"

async def test_payload(payload):
    uri = "wss://us-central1-autopush-aiplatform.sandbox.googleapis.com/ws/google.cloud.aiplatform.v1beta1.LlmBidiService/BidiGenerateContent"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        async with websockets.connect(uri, additional_headers=headers) as ws:
            print("Connected, sending setup...")
            await ws.send(json.dumps(payload))
            resp = await ws.recv()
            print("Setup response:", resp[:200])
            return True
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Closed with {e.code}: {e.reason}")
        return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

async def main():
    print("Test 1: Sastain payload exact match")
    p1 = {
        "setup": {
            "systemInstruction": {"parts": [{"text": "You are a chef."}]},
            "model": "projects/cloud-llm-preview1/locations/us-central1/publishers/google/models/gemini-3.1-flash-live-preview-04-2026",
            "avatarConfig": {
                "avatar_name": "Ben"
            },
            "generationConfig": {
                "responseModalities": ["VIDEO"],
                "speechConfig": {
                    "voiceConfig": {
                        "prebuiltVoiceConfig": {"voiceName": "Puck"}
                    },
                    "languageCode": "en-US"
                }
            },
            "inputAudioTranscription": {},
            "outputAudioTranscription": {},
            "tools": [
                { "googleSearch": {} },
                {
                    "functionDeclarations": [
                        {
                            "name": "recipe_lookup_agent",
                            "description": "Searches for recipes based on cart items using Google Search.",
                            "parameters": {
                                "type": "OBJECT",
                                "properties": {
                                    "cart_items": {"type": "ARRAY", "items": {"type": "STRING"}}
                                },
                                "required": ["cart_items"]
                            }
                        }
                    ]
                }
            ]
        }
    }
    await test_payload(p1)

    print("\nTest 2: Without transcriptions but with tools")
    p2 = {
        "setup": {
            "model": "projects/cloud-llm-preview1/locations/us-central1/publishers/google/models/gemini-3.1-flash-live-preview-04-2026",
            "avatarConfig": {
                "avatar_name": "Ben"
            },
            "generationConfig": {
                "responseModalities": ["VIDEO"],
                "speechConfig": {
                    "voiceConfig": {
                        "prebuiltVoiceConfig": {"voiceName": "Puck"}
                    },
                    "languageCode": "en-US"
                }
            },
            "tools": [
                { "googleSearch": {} }
            ]
        }
    }
    await test_payload(p2)

    
    print("\nTest 3: responseModalities AUDIO")
    p3 = {
        "setup": {
            "model": "projects/cloud-llm-preview1/locations/us-central1/publishers/google/models/gemini-3.1-flash-live-preview-04-2026",
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
    await test_payload(p3)

asyncio.run(main())
