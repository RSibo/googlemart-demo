"""Main FastAPI application for GoogleMart with robust path handling."""

import asyncio
import json
import os
from fastapi import FastAPI, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

static_dir = "/google/src/cloud/rsibo/googlemart-virtual-chef-adk/google3/labs/language/genai/agents/googlemart/static"
templates_dir = "/google/src/cloud/rsibo/googlemart-virtual-chef-adk/google3/labs/language/genai/agents/googlemart/templates"
print(f"DEBUG: static_dir={static_dir}")
print(f"DEBUG: templates_dir={templates_dir}")

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Setup templates
templates = Jinja2Templates(directory=templates_dir)

from google3.labs.language.genai.agents.googlemart.mock_data import MOCK_CART, PRODUCTS, RECIPES
from google3.labs.language.genai.agents.googlemart.sous_chefs import meal_planner, nutritionist, pantry_scout, sommelier

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "products": PRODUCTS})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Send initial greeting
    await websocket.send_text(json.dumps({
        "type": "text",
        "content": "Hello! I am your GoogleMart Executive Chef. How can I help you today?"
    }))
    
    while True:
        data = await websocket.receive_text()
        try:
            message = json.loads(data)
            user_text = message.get("content", "").lower()
            
            response_text = ""
            
            if "what can i make" in user_text or "cart" in user_text:
                recipes = meal_planner(MOCK_CART)
                response_text = "Based on your cart, here are some recipes you can make:\n"
                for r in recipes:
                    response_text += f"- **{r['name']}**\n"
                
                # Suggest missing ingredients (Pantry Scout)
                staples = pantry_scout(MOCK_CART)
                if staples:
                    response_text += "\nIt looks like you might also need: "
                    response_text += ", ".join([PRODUCTS[s]["name"] for s in staples])
                    
            elif "beef" in user_text and "healthy" in user_text:
                info = nutritionist("SKU_BEEF")
                response_text = f"The {info['name']} has {info['macros'].get('protein')}g of protein per serving. "
                response_text += "It's a great base for a Bolognese, which is usually a hit with kids!"
                
            elif "steak" in user_text:
                pairings = sommelier("SKU_STEAK")
                response_text = "Excellent choice on the Ribeye! I recommend pairing it with "
                response_text += ", ".join([PRODUCTS[p]["name"] for p in pairings if p != "SKU_STEAK"])
                
            else:
                response_text = "I'm not sure I understand. I can help you with recipes based on your cart, nutrition info, or pairings."
                
            # Simulate typing latency
            await asyncio.sleep(1)
            
            await websocket.send_text(json.dumps({
                "type": "text",
                "content": response_text
            }))
            
        except Exception as e:
            await websocket.send_text(json.dumps({
                "type": "error",
                "content": f"Error: {str(e)}"
            }))
            break

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
