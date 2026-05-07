"""Main FastAPI application for GoogleMart with robust path handling."""

import asyncio
import json
import os
import websockets
import fastapi
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

static_dir = "/google/src/cloud/rsibo/googlemart-virtual-chef-adk/google3/labs/language/genai/agents/googlemart/frontend/dist"
assets_dir = "/google/src/cloud/rsibo/googlemart-virtual-chef-adk/google3/labs/language/genai/agents/googlemart/frontend/dist/assets"

app = fastapi.FastAPI()

# Serve React assets
app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
# Also keep old static for magic_icon.png if needed, or better move it to frontend/public
# For now let's mount the old static as well
app.mount("/static", StaticFiles(directory="/google/src/cloud/rsibo/googlemart-virtual-chef-adk/google3/labs/language/genai/agents/googlemart/static"), name="static")

# Setup templates to point to React's dist
templates = Jinja2Templates(directory=static_dir)

from google3.labs.language.genai.agents.googlemart.mock_data import MOCK_CART, PRODUCTS, RECIPES
from google3.labs.language.genai.agents.googlemart.sous_chefs import (
    run_recipe_lookup, nutritionist, pantry_scout, sommelier
)

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
        token = config.get("accessToken")
        project = config.get("projectId")
        location = config.get("location", "us-central1")
        model_id = config.get("modelId", "gemini-3.1-flash-live-preview-04-2026")
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
                "systemInstruction": {"parts": [{"text": CHEF_INSTRUCTION}]},
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
        await gemini_ws.send(json.dumps(setup_msg))
        await gemini_ws.recv() # Wait for setup acknowledgment

        # Send initial greeting prompt to Gemini to kick off the conversation
        greeting_msg = {
            "clientContent": {
                "turns": [
                    {
                        "role": "user",
                        "parts": [{"text": "Hello, I have just connected. Please introduce yourself warmly as the Virtual Chef and ask how you can help me today."}]
                    }
                ],
                "turnComplete": True
            }
        }
        await gemini_ws.send(json.dumps(greeting_msg))

        # Start proxy loops
        async def client_to_gemini():
            try:
                while True:
                    data = await websocket.receive_text()
                    msg = json.loads(data)

                    if msg.get("type") == "cart_update":
                        # Send a hidden context message to Gemini about the cart change
                        cart_skus = msg.get("content", [])
                        cart_details = [f"{PRODUCTS[sku]['name']} (${PRODUCTS[sku]['price']:.2f})" for sku in cart_skus if sku in PRODUCTS]
                        cart_text = ", ".join(cart_details) if cart_details else "Empty"
                        
                        gemini_msg = {
                            "clientContent": {
                                "turns": [
                                    {
                                        "role": "user",
                                        "parts": [{"text": f"[CONTEXT: The user's shopping cart has been updated. Current contents: {cart_text}. Please use this information if the user asks about their cart.]"}]
                                    }
                                ],
                                "turnComplete": True
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
                            "clientContent": {
                                "turns": [
                                    {
                                        "role": "user",
                                        "parts": [{"text": f"[CONTEXT: The user is currently viewing these products on their screen: {visible_text}. Please use this information if the user asks about what they are looking at or what is on the screen.]"}]
                                    }
                                ],
                                "turnComplete": True
                            }
                        }
                        await gemini_ws.send(json.dumps(gemini_msg))

                    elif "content" in msg and not msg.get("type"):
                        # Only send content as realtime input if it's explicitly meant to be speech/text input (no type specified, or handled as user text)
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
                print(f"Error in gemini_to_client: {e}")        # Run both loops concurrently
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
