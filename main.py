"""Main FastAPI application for GoogleMart with robust path handling."""

import asyncio
import json
import os
import websockets
import fastapi
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

static_dir = "/google/src/cloud/rsibo/googlemart-virtual-chef-adk/google3/labs/language/genai/agents/googlemart/static"
templates_dir = "/google/src/cloud/rsibo/googlemart-virtual-chef-adk/google3/labs/language/genai/agents/googlemart/templates"
print(f"DEBUG: static_dir={static_dir}")
print(f"DEBUG: templates_dir={templates_dir}")

app = fastapi.FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Setup templates
templates = Jinja2Templates(directory=templates_dir)

from google3.labs.language.genai.agents.googlemart.mock_data import MOCK_CART, PRODUCTS, RECIPES
from google3.labs.language.genai.agents.googlemart.sous_chefs import meal_planner, nutritionist, pantry_scout, sommelier

@app.get("/")
async def read_root(request: fastapi.Request):
    return templates.TemplateResponse("index.html", {"request": request, "products": PRODUCTS})

@app.websocket("/ws")
async def websocket_endpoint(websocket: fastapi.WebSocket):
    await websocket.accept()
    
    gemini_ws = None
    
    try:
        # Wait for setup message
        data = await websocket.receive_text()
        message = json.loads(data)
        
        if message.get("type") != "setup":
            await websocket.send_text(json.dumps({
                "type": "error",
                "content": "Expected setup message first."
            }))
            await websocket.close()
            return
            
        config = message.get("content", {})
        token = config.get("accessToken")
        project = config.get("projectId")
        location = config.get("location", "us-central1")
        model_id = config.get("modelId", "gemini-3.1-flash-live-preview")
        voice = config.get("voice", "Puck")
        avatar = config.get("avatar", "Ben")
        
        # Construct URI
        host = f"{location}-autopush-aiplatform.sandbox.googleapis.com"
        uri = f"wss://{host}/ws/google.cloud.aiplatform.v1.LlmBidiService/BidiGenerateContent"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Connect to Gemini
        gemini_ws = await websockets.connect(uri, additional_headers=headers)
        
        # Send setup message to Gemini
        model_path = f"projects/{project}/locations/{location}/publishers/google/models/{model_id}"
        setup_msg = {
            "setup": {
                "systemInstruction": {"parts": [{"text": "You are a helpful AI assistant."}]},
                "model": model_path,
                "generationConfig": {
                    "responseModalities": ["VIDEO"],
                    "speechConfig": {
                        "voiceConfig": {
                            "prebuiltVoiceConfig": {"voiceName": voice}
                        }
                    }
                },
                "avatarConfig": {
                    "avatar_name": avatar
                }
            }
        }
        await gemini_ws.send(json.dumps(setup_msg))
        await gemini_ws.recv() # Wait for setup acknowledgment
        
        # Send initial greeting to client
        await websocket.send_text(json.dumps({
            "type": "text",
            "content": f"Connected to Gemini Live Avatar! I am using avatar {avatar} and voice {voice}."
        }))
        
        # Start proxy loops
        async def client_to_gemini():
            try:
                while True:
                    data = await websocket.receive_text()
                    msg = json.loads(data)
                    if "content" in msg:
                        gemini_msg = {
                            "realtime_input": {
                                "text": msg["content"]
                            }
                        }
                        await gemini_ws.send(json.dumps(gemini_msg))
            except fastapi.WebSocketDisconnect:
                pass
            except Exception as e:
                print(f"Error in client_to_gemini: {e}")
                
        async def gemini_to_client():
            try:
                async for message in gemini_ws:
                    response = json.loads(message)
                    
                    parts = response.get("serverContent", {}).get("modelTurn", {}).get("parts", [])
                    for part in parts:
                        if "inlineData" in part:
                            # Send video frame to client
                            await websocket.send_text(json.dumps({
                                "type": "video",
                                "content": part["inlineData"]["data"]
                            }))
                            
                        if "text" in part:
                            await websocket.send_text(json.dumps({
                                "type": "text",
                                "content": part["text"]
                            }))
                            
            except Exception as e:
                print(f"Error in gemini_to_client: {e}")
                
        # Run both loops concurrently
        await asyncio.gather(client_to_gemini(), gemini_to_client())
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "content": f"Connection error: {str(e)}"
        }))
    finally:
        if gemini_ws:
            await gemini_ws.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
