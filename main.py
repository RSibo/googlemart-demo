"""Main FastAPI application for GoogleMart with robust path handling."""

import asyncio
import json
import os
import websockets
import fastapi
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import traceback

current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = "labs/language/genai/agents/googlemart/frontend/dist"
assets_dir = "labs/language/genai/agents/googlemart/frontend/dist/assets"

print(f"DEBUG: current_dir={current_dir}")
print(f"DEBUG: static_dir={static_dir}, exists={os.path.exists(static_dir)}")
print(f"DEBUG: assets_dir={assets_dir}, exists={os.path.exists(assets_dir)}")
try:
    print(f"DEBUG: files in assets_dir={os.listdir(assets_dir)}")
except Exception as e:
    print(f"DEBUG: failed to list assets_dir: {e}")
print(f"DEBUG: cwd={os.getcwd()}")
app = fastapi.FastAPI()

# Serve React assets
app.mount("/assets", StaticFiles(directory="/google/src/cloud/rsibo/googlemart-virtual-chef-adk/google3/labs/language/genai/agents/googlemart/static/assets"), name="assets")
# Also keep old static for magic_icon.png if needed, or better move it to frontend/public
# For now let's mount the old static as well
app.mount("/static", StaticFiles(directory="/google/src/cloud/rsibo/googlemart-virtual-chef-adk/google3/labs/language/genai/agents/googlemart/static"), name="static")

# Setup templates to point to React's dist
templates = Jinja2Templates(directory="/google/src/cloud/rsibo/googlemart-virtual-chef-adk/google3/labs/language/genai/agents/googlemart/templates")

from google3.labs.language.genai.agents.googlemart.mock_data import MOCK_CART, PRODUCTS, RECIPES
from google3.labs.language.genai.agents.googlemart.sous_chefs import (
    run_recipe_lookup, nutritionist, pantry_scout, sommelier
)
from google3.labs.language.genai.agents.googlemart.orchestrator import ExecutiveChef
from google3.learning.agents.orcas.framework.runners.secure_runner import InMemorySecureRunner

from google.genai import types as adk_types
CHEF_INSTRUCTION = """
You are the Executive Chef of GoogleMart, a grocery chain in Australia.
You maintain a warm, professional, and helpful chef persona.
You help users with:
1. Basket Transformation: Suggesting recipes based on cart contents.
2. Healthy Filter: Providing nutritional information and health tips.
3. Complete the Meal: Suggesting pairings and upsells.

Use your Sous-Chefs (sub-agents and tools) to gather information:
- `recipe_lookup_agent`: Finds recipes based on cart items using Google Search.
- `nutritionist`: Provides macros and allergen info for a product.
- `pantry_scout`: Checks for staples based on cart items.
- `sommelier`: Suggests pairings for a product.

Always respond in character as a friendly and expert chef.
"""


@app.get("/")
async def read_root(request: fastapi.Request):
    return templates.TemplateResponse("index.html", {"request": request, "products": PRODUCTS})

@app.get("/api/products")
async def get_products():
    return PRODUCTS

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
        token = config.get("accessToken", "").strip().strip('"').strip("'")
        project = config.get("projectId") or "cloud-llm-preview1"
        location = config.get("location") or "us-central1"
        model_id = config.get("modelId") or "gemini-3.1-flash-live-preview-04-2026"
        if model_id == "gemini_live_rev25_ava":
            model_id = "gemini-3.1-flash-live-preview-04-2026"
        voice = config.get("voice") or "Puck"
        avatar = config.get("avatar") or "Ben"
        from google.adk.models.google_llm import Gemini
        from google.genai import Client
        from google.genai import types
        
        from google.auth.credentials import Credentials
        
        class SimpleTokenCredentials(Credentials):
            def __init__(self, token):
                super().__init__()
                self.token = token
                
            def apply(self, headers, token_type='Bearer'):
                headers['Authorization'] = f'{token_type} {self.token}'
                
            def before_request(self, request, method, url, headers):
                self.apply(headers)
                
            def refresh(self, request):
                pass

        from functools import cached_property
        class TokenGemini(Gemini):
            @cached_property
            def api_client(self) -> Client:
                headers = self._tracking_headers()
                
                kwargs = {
                    'http_options': types.HttpOptions(headers=headers),
                    'vertexai': True,
                    'project': project,
                    'location': location,
                    'credentials': SimpleTokenCredentials(token)
                }
                return Client(**kwargs)
                
        adk_model = TokenGemini(model="gemini-2.5-flash")
        chef = ExecutiveChef(model=adk_model)
        chef_agent = chef.get_agent()

        from google3.learning.agents.orcas.framework.runners.secure_runner import SecureRunner
        from google.adk.sessions.in_memory_session_service import InMemorySessionService
        from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
        from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
        
        session_service = InMemorySessionService()
        
        runner = SecureRunner(
            agent=chef_agent,
            app_name="chef_app",
            session_service=session_service,
            artifact_service=InMemoryArtifactService(),
            memory_service=InMemoryMemoryService(),
            auto_create_session=True
        )
        # Construct URI
        host = f"{location}-autopush-aiplatform.sandbox.googleapis.com"
        uri = f"wss://{host}/ws/google.cloud.aiplatform.v1.LlmBidiService/BidiGenerateContent"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Save token for local testing
        with open("/tmp/gemini_token.txt", "w") as f:
            f.write(token)

        print(f"DEBUG: Connecting to Gemini API at {uri}")
        # Connect to Gemini
        gemini_ws = await websockets.connect(uri, additional_headers=headers)
        print("DEBUG: Connected to Gemini API successfully")

        # Send setup message to Gemini
        model_path = f"projects/{project}/locations/{location}/publishers/google/models/{model_id}"
        setup_msg = {
            "setup": {
                "systemInstruction": {"parts": [{"text": CHEF_INSTRUCTION}]},
                "model": model_path,
                "generationConfig": {
                    "responseModalities": ["AUDIO", "VIDEO"],
                    "speechConfig": {
                        "voiceConfig": {
                            "prebuiltVoiceConfig": {"voiceName": voice}
                        },
                        "languageCode": "en-US"
                    }
                },
                "avatarConfig": {
                    "avatar_name": avatar
                },
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
                            },
                            {
                                "name": "nutritionist",
                                "description": "Provides macros and allergen alerts for a specific product.",
                                "parameters": {
                                    "type": "OBJECT",
                                    "properties": {
                                        "product_sku": {"type": "STRING"}
                                    },
                                    "required": ["product_sku"]
                                }
                            },
                            {
                                "name": "pantry_scout",
                                "description": "Analyzes the basket and identifies missing staples.",
                                "parameters": {
                                    "type": "OBJECT",
                                    "properties": {
                                        "cart_items": {"type": "ARRAY", "items": {"type": "STRING"}}
                                    },
                                    "required": ["cart_items"]
                                }
                            },
                            {
                                "name": "sommelier",
                                "description": "Handles flavor pairings (wines, sides).",
                                "parameters": {
                                    "type": "OBJECT",
                                    "properties": {
                                        "product_sku": {"type": "STRING"}
                                    },
                                    "required": ["product_sku"]
                                }
                            },
                            {
                                "name": "suggest_product",
                                "description": "Suggests a specific product to the user with an interactive button in the chat.",
                                "parameters": {
                                    "type": "OBJECT",
                                    "properties": {
                                        "sku": {"type": "STRING", "description": "The SKU of the product to suggest."}
                                    },
                                    "required": ["sku"]
                                }
                            },
                            {
                                "name": "show_recipe",
                                "description": "Displays a rich recipe card in a popup panel for the user.",
                                "parameters": {
                                    "type": "OBJECT",
                                    "properties": {
                                        "name": {"type": "STRING", "description": "Name of the recipe."},
                                        "ingredients": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "List of ingredient descriptions."},
                                        "instructions": {"type": "STRING", "description": "Step by step instructions."},
                                        "prep_time": {"type": "STRING", "description": "Estimated preparation time."}
                                    },
                                    "required": ["name", "ingredients", "instructions"]
                                }
                            }
                        ]
                    }
                ]
            }
        }
        
        print(f"DEBUG: exact setup_msg: {json.dumps(setup_msg)}")
        await gemini_ws.send(json.dumps(setup_msg))
        await gemini_ws.recv() # Wait for setup acknowledgment

        # Send initial greeting prompt to Gemini to kick off the conversation
        greeting_msg = {
            "realtime_input": {
                "text": "Hello, I have just connected. Please introduce yourself warmly as the Virtual Chef and ask how you can help me today."
            }
        }
        await gemini_ws.send(json.dumps(greeting_msg))

        # Start proxy loops
        async def client_to_gemini():
            try:
                while True:
                    data = await websocket.receive_text()
                    msg = json.loads(data)
                    print(f"DEBUG: Msg from client: {msg.get('type', 'text')}")

                    if msg.get("type") == "cart_update":
                        # Send a hidden context message to Gemini about the cart change
                        cart_skus = msg.get("content", [])
                        cart_details = [f"{PRODUCTS[sku]['name']} (${PRODUCTS[sku]['price']:.2f})" for sku in cart_skus if sku in PRODUCTS]
                        cart_text = ", ".join(cart_details) if cart_details else "Empty"
                        
                        gemini_msg = {
                            "realtime_input": {
                                "text": f"[CONTEXT: The user's shopping cart has been updated. Current contents: {cart_text}. Please use this information if the user asks about their cart.]"
                            }
                        }
                        await gemini_ws.send(json.dumps(gemini_msg))

                    elif msg.get("type") == "context_update":
                        # Send a hidden context message to Gemini about the visible screen
                        visible_skus_str = msg.get("content", "")
                        # Frontend sends "User is currently viewing: SKU_..., SKU_..."
                        skus = []
                        if ":" in visible_skus_str:
                            skus_part = visible_skus_str.split(":", 1)[1]
                            skus = [s.strip() for s in skus_part.split(",")]
                        
                        visible_details = [f"{PRODUCTS[sku]['name']} (${PRODUCTS[sku]['price']:.2f})" for sku in skus if sku in PRODUCTS]
                        visible_text = ", ".join(visible_details) if visible_details else "Nothing specific"
                        
                        gemini_msg = {
                            "realtime_input": {
                                "text": f"[CONTEXT: The user is currently viewing these products on their screen: {visible_text}. Please use this information if the user asks about what they are looking at or what is on the screen.]"
                            }
                        }
                        await gemini_ws.send(json.dumps(gemini_msg))

                    elif "content" in msg and not msg.get("type"):
                        user_msg = msg["content"]
                        response_text = ""
                        try:
                            async for event in runner.run_async(
                                user_id="chef_user", session_id="session_1",
                                new_message=adk_types.Content(role="user", parts=[adk_types.Part.from_text(text=user_msg)]),
                            ):
                                if event.is_final_response() and event.content.parts:
                                    response_text = event.content.parts[0].text
                            
                            print(f"DEBUG: ADK Agent response: {response_text}")
                            
                            # Send response to Gemini Live to speak it
                            gemini_msg = {
                                "clientContent": {
                                    "turns": [
                                        {
                                            "role": "user",
                                            "parts": [{"text": response_text}]
                                        }
                                    ],
                                    "turnComplete": True
                                }
                            }
                            await gemini_ws.send(json.dumps(gemini_msg))
                            
                            # Also send text response to client UI so they see it!
                            await websocket.send_text(json.dumps({
                                "type": "text",
                                "content": response_text
                            }))
                            
                        except Exception as e:
                            tb = traceback.format_exc()
                            print(f"Error running ADK agent:\n{tb}")
                            await websocket.send_text(json.dumps({
                                "type": "error",
                                "content": f"Error running ADK agent: {str(e)}\n{tb}"
                            }))
            except fastapi.WebSocketDisconnect:
                pass
            except Exception as e:
                print(f"Error in client_to_gemini: {e}")
                try:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "content": f"Error in client_to_gemini: {str(e)}"
                    }))
                except:
                    pass

        async def gemini_to_client():
            try:
                async for message in gemini_ws:
                    response = json.loads(message)

                    parts = response.get("serverContent", {}).get("modelTurn", {}).get("parts", [])
                    for part in parts:
                        if "inlineData" in part:
                            mime_type = part["inlineData"].get("mimeType", "")
                            data = part["inlineData"]["data"]
                            
                            if "image" in mime_type or not mime_type: # Fallback to video if no mimeType as before
                                await websocket.send_text(json.dumps({
                                    "type": "video",
                                    "content": data
                                }))
                            elif "audio" in mime_type:
                                await websocket.send_text(json.dumps({
                                    "type": "audio",
                                    "content": data
                                }))

                        if "text" in part:
                            await websocket.send_text(json.dumps({
                                "type": "text",
                                "content": part["text"]
                            }))

                        if "functionCall" in part:
                            fn_name = part["functionCall"]["name"]
                            args = part["functionCall"].get("args", {})
                            print(f"Tool call received: {fn_name} with {args}")

                            result = {"status": "success"}

                            if fn_name == "recipe_lookup_agent":
                                result = await run_recipe_lookup(args.get("cart_items", []), None)
                            elif fn_name == "nutritionist":
                                result = nutritionist(args.get("product_sku", ""))
                            elif fn_name == "pantry_scout":
                                result = pantry_scout(args.get("cart_items", []))
                            elif fn_name == "sommelier":
                                result = sommelier(args.get("product_sku", ""))
                            elif fn_name == "suggest_product":
                                # Proxy to UI
                                await websocket.send_text(json.dumps({
                                    "type": "product_suggestion",
                                    "content": args.get("sku")
                                }))
                            elif fn_name == "show_recipe":
                                # Proxy to UI
                                await websocket.send_text(json.dumps({
                                    "type": "show_ui",
                                    "component": "recipe_card",
                                    "props": args
                                }))

                            print(f"Tool call result: {result}")

                            call_id = part["functionCall"].get("id")
                            func_resp_part = {
                                "functionResponse": {
                                    "name": fn_name,
                                    "response": {"result": result}
                                }
                            }
                            if call_id:
                                func_resp_part["functionResponse"]["id"] = call_id

                            tool_resp_msg = {
                                "clientContent": {
                                    "turns": [
                                        {
                                            "role": "user",
                                            "parts": [
                                                func_resp_part
                                            ]
                                        }
                                    ],
                                    "turnComplete": True
                                }
                            }
                            await gemini_ws.send(json.dumps(tool_resp_msg))

            except Exception as e:
                print(f"Error in gemini_to_client: {e}")
                try:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "content": f"Error in gemini_to_client: {str(e)}"
                    }))
                except:
                    pass        # Run both loops concurrently
        await asyncio.gather(client_to_gemini(), gemini_to_client())
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "content": f"Connection error: {str(e)}"
        }))
        await websocket.close()
    finally:
        if gemini_ws:
            await gemini_ws.close()
app.mount("/", StaticFiles(directory=static_dir), name="root_static")
if __name__ == "__main__":
    from absl import flags
    import sys
    try:
        flags.FLAGS(sys.argv)
    except flags.UnrecognizedFlagError:
        flags.FLAGS(['main.py'])
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)
