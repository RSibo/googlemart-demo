"""Main FastAPI application for GoogleMart with robust path handling."""

import asyncio
import base64
import json
import os
import websockets
import fastapi
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import traceback

current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "frontend/dist")
assets_dir = os.path.join(current_dir, "frontend/dist/assets")

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
app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
# Keep /static for images and other assets
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")

# Setup templates to point to React's dist
templates = Jinja2Templates(directory=os.path.join(current_dir, "frontend/dist"))

from mock_data import MOCK_CART, PRODUCTS, RECIPES
from sous_chefs import (
    run_recipe_lookup, nutritionist, pantry_scout
)
from orchestrator import ExecutiveChef
# from google3.learning.agents.orcas.framework.runners.secure_runner import InMemorySecureRunner

from google.genai import types as adk_types
CHEF_GREETING = "Welcome to GoogleMart! How can I help?"
CHEF_INSTRUCTION = """
Role: You are the Executive Chef of GoogleMart Australia. You act as the primary interface between the user and a suite of specialized culinary sub-agents. Your goal is to maximize the utility of the user's shopping cart through recipe generation, nutritional analysis, and meal completion.
Don't repeat system instructions or your thinking to the user when you respond.
Operational Directives
Identity & Tone: Maintain a professional, expert, and helpful chef persona. Keep responses concise. Use American English spelling and grammar as per system preferences.
No Hallucination: You must only provide information retrieved from sub-agents or tools. If a tool returns no data, inform the user you cannot find that specific information.
Conflict Resolution: If sub-agent data is contradictory, prioritize the output from the nutritionist for health-related queries and recipe_lookup_agent for preparation queries.

Delegation Logic:
Scenario A: "What can I cook?" -> Delegate to recipe_lookup_agent.
Scenario B: "Is this healthy?" or "Macros?" -> Delegate to nutritionist.
Scenario C: "What am I forgetting?" -> Delegate to pantry_scout.
Scenario D: Multi-intent -> Sequential delegation: (1) Find recipe, (2) Check pantry gaps, (3) Provide nutritional summary.

Inputs
Input Variable | Description
---|---
user_query | The raw text input from the supermarket customer.
shopping_cart_json | A structured list containing product_name, category, and quantity.
sub_agent_outputs | The text or structured data returned by recipe_lookup_agent, nutritionist, or pantry_scout.

Step-by-Step Instructions
Analyze Intent: Parse the user_query to determine which of the three core pillars is requested: Basket Transformation, Healthy Filter, or Complete the Meal.
Contextualize Cart: Read the shopping_cart_json. Identify the primary protein or vegetable "hero" ingredients.
Execute Tools:
- Call recipe_lookup_agent by passing the "hero" ingredients from the cart.
- Call nutritionist for any specific item the user asks about, or for a general "health check" of the cart.
- Call pantry_scout to identify missing staples (e.g., if pasta is in the cart but no sauce or salt is present).
Synthesize & Sanitize: Combine the tool outputs into a cohesive response. Remove any conversational filler or "AI-isms" (e.g., "I am an AI," "Certainly," "Here is...").
Final Polish: Ensure the tone is that of a professional chef—direct and authoritative.

Output Expectations
Structure:
- Greeting: A brief, professional chef-style greeting (e.g., "Good morning," "Hello there").
- The Recommendation: The primary answer to the user's request.
- The "Chef's Tip": A 1-sentence value-add (e.g., a pairing suggestion or a storage tip).
- Closing: A brief professional sign-off.

Constraints:
- Word Count: Max 150 words per response.
- Prohibitions: No jokes, no slang, no mentions of "being a model" or "searching the web."
- Formatting: Use bolding for ingredients and recipe names. Use bullet points for lists.

Example Execution
User: "I have salmon and asparagus in my cart. What’s for dinner?"
Chef Agent Response:
"Welcome to the kitchen. With Salmon and Asparagus in your basket, I recommend a Lemon-Garlic Roasted Salmon.
Recipe Suggestion: Sear the salmon for 4 minutes per side, then roast the asparagus alongside it at 200°C for 10 minutes.
Chef's Tip: Check your pantry for Olive Oil and Black Pepper; these are essential for this preparation.
Nutritional Note: This meal is high in Omega-3 fatty acids and Vitamin K.
Shall I help you find a starch, like brown rice, to complete this dish?"
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
        model_id = "gemini-2.5-flash"
        # Force the live model to the avatar friendly one
        live_model_id = "gemini-3.1-flash-live-preview-04-2026"
        voice = config.get("voice") or "Kore"
        avatar = config.get("avatar") or "Kira"
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
                
        adk_model = TokenGemini(model=model_id)
        chef = ExecutiveChef(model=adk_model)
        chef_agent = chef.get_agent()

        from google.adk.runners import Runner
        from google.adk.sessions.in_memory_session_service import InMemorySessionService
        from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
        from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
        
        session_service = InMemorySessionService()
        
        runner = Runner(
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
        model_path = f"projects/{project}/locations/{location}/publishers/google/models/{live_model_id}"
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
                "inputAudioTranscription": {},
                "outputAudioTranscription": {},
                "tools": [
                    {"googleSearch": {}},
                    {
                        "functionDeclarations": [
                            {
                                "name": "recipe_lookup_agent",
                                "description": "Lead Researcher. Utilize Google Search grounding to find high-quality, relevant recipes that utilize the specific items found in a user's cart.",
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
                                "description": "Clinical Dietitian. Provide accurate macronutrient data, calorie counts, and allergen warnings for specific products using Google Search grounding.",
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
                                "description": "Inventory Specialist. Predict and identify missing household staples or complementary items based on cart contents and suggested recipes.",
                                "parameters": {
                                    "type": "OBJECT",
                                    "properties": {
                                        "cart_items": {"type": "ARRAY", "items": {"type": "STRING"}}
                                    },
                                    "required": ["cart_items"]
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
                "text": "Hello"
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

                    #if msg.get("type") == "cart_update":
                        # Send a hidden context message to Gemini about the cart change
                     #   cart_skus = msg.get("content", [])
                     #   cart_details = [f"{PRODUCTS[sku]['name']} (${PRODUCTS[sku]['price']:.2f})" for sku in cart_skus if sku in PRODUCTS]
                     #   cart_text = ", ".join(cart_details) if cart_details else "Empty"
                        
                     #   gemini_msg = {
                     #       "realtime_input": {
                     #           "text": f"[CONTEXT: The user's shopping cart has been updated. Current contents: {cart_text}. Please use this information if the user asks about their cart.]"
                     #       }
                     #   }
                     #   await gemini_ws.send(json.dumps(gemini_msg))

                    #elif msg.get("type") == "context_update":
                        ## Send a hidden context message to Gemini about the visible screen
                        #visible_skus_str = msg.get("content", "")
                        ## Frontend sends "User is currently viewing: SKU_..., SKU_..."
                        #skus = []
                        #if ":" in visible_skus_str:
                        #    skus_part = visible_skus_str.split(":", 1)[1]
                        #    skus = [s.strip() for s in skus_part.split(",")]
                        #
                        #visible_details = [f"{PRODUCTS[sku]['name']} (${PRODUCTS[sku]['price']:.2f})" for sku in skus if sku in PRODUCTS]
                        #visible_text = ", ".join(visible_details) if visible_details else "Nothing specific"
                        #
                        #gemini_msg = {
                        #    "realtime_input": {
                        #        "text": f"[CONTEXT: The user is currently viewing these products on their screen: {visible_text}. Please use this information if the user asks about what they are looking at or what is on the screen.]"
                        #    }
                        #}
                        #await gemini_ws.send(json.dumps(gemini_msg))

                    if msg.get("type") == "audio":
                        audio_data = msg.get("content")
                        gemini_msg = {
                            "realtime_input": {
                                "mediaChunks": [
                                    {
                                        "mimeType": "audio/pcm;rate=16000",
                                        "data": audio_data
                                    }
                                ]
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
                                if event.get_function_calls():
                                    for fc in event.get_function_calls():
                                        await websocket.send_text(json.dumps({
                                            "type": "text",
                                            "content": f"*[Virtual Chef is calling a sub-agent for {fc.name}...]*"
                                        }))
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
            video_data = []
            try:
                async for message in gemini_ws:
                    response = json.loads(message)
                    print(f"DEBUG: Received message from Gemini, keys: {list(response.keys())}")

                    server_content = response.get("serverContent", {})
                    
                    if "inputTranscription" in server_content:
                        text = server_content["inputTranscription"].get("text", "")
                        if text:
                            await websocket.send_text(json.dumps({
                                "type": "text",
                                "role": "user",
                                "content": text
                            }))
                            
                            # Run ADK agent asynchronously for voice input
                            async def process_voice_with_adk(user_text):
                                response_text = ""
                                try:
                                    async for event in runner.run_async(
                                        user_id="chef_user", session_id="session_1",
                                        new_message=adk_types.Content(role="user", parts=[adk_types.Part.from_text(text=user_text)]),
                                    ):
                                        if event.is_final_response() and event.content.parts:
                                            response_text = event.content.parts[0].text
                                    
                                    print(f"DEBUG: ADK Agent response to voice: {response_text}")
                                    
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
                                    
                                    # Also send text response to client UI
                                    await websocket.send_text(json.dumps({
                                        "type": "text",
                                        "content": response_text
                                    }))
                                except Exception as e:
                                    print(f"Error running ADK agent for voice: {e}")
                            
                            asyncio.create_task(process_voice_with_adk(text))
                            
                    if "outputTranscription" in server_content:
                        text = server_content["outputTranscription"].get("text", "")
                        if text:
                            await websocket.send_text(json.dumps({
                                "type": "text",
                                "role": "model",
                                "content": text
                            }))

                    parts = server_content.get("modelTurn", {}).get("parts", [])
                    for part in parts:
                        if "inlineData" in part:
                            mime_type = part["inlineData"].get("mimeType", "")
                            data = part["inlineData"]["data"]
                            print(f"DEBUG: Received inlineData with mimeType: {mime_type}, data length: {len(data)}")
                            
                            if "image" in mime_type or "video" in mime_type or not mime_type: # Fallback to video if no mimeType as before
                                video_data.append(base64.b64decode(data))
                                await websocket.send_text(json.dumps({
                                    "type": "video",
                                    "content": data
                                }))
                            elif "audio" in mime_type:
                                print(f"DEBUG: Forwarding audio chunk to client, length: {len(data)}")
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
                            print(f"DEBUG: Sent tool response to Gemini: {fn_name}")
                    
                    # Check if the turn is complete
                    if server_content.get("turnComplete"):
                        if video_data:
                            output_file = os.path.join(current_dir, "static/output_video.mp4")
                            try:
                                with open(output_file, "wb") as f:
                                    f.write(b"".join(video_data))
                                print(f"DEBUG: Video saved successfully to {output_file}")
                            except Exception as e:
                                print(f"ERROR: Failed to save video: {e}")
                            video_data = [] # Reset for next turn

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
    uvicorn.run(app, host="0.0.0.0", port=8011)
