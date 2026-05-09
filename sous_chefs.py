"""Sous Chefs for GoogleMart."""

from google3.labs.language.genai.agents.googlemart.mock_data import PRODUCTS, RECIPES

async def run_recipe_lookup(cart_items: list[str]) -> str:
    """Mock implementation of recipe lookup."""
    return "Based on your cart, I suggest making a delicious Chicken Alfredo or a Fresh Salad."

def nutritionist(product_sku: str) -> dict:
    """Provides macros and allergen alerts for a specific product."""
    product = PRODUCTS.get(product_sku)
    if not product:
        return {"error": "Product not found"}
        
    return {
        "name": product["name"],
        "macros": product.get("macros", {}),
        "allergens": product.get("allergens", [])
    }

def pantry_scout(cart_items: list[str]) -> list[str]:
    """Analyzes the basket and identifies missing staples."""
    # Example: if buying flour and sugar, suggest baking powder and vanilla
    cart_skus = set(cart_items)
    suggestions = []
    
    if "SKU_FLOUR" in cart_skus and "SKU_SUGAR" in cart_skus:
        if "SKU_BAKING_POWDER" not in cart_skus:
            suggestions.append("SKU_BAKING_POWDER")
        if "SKU_VANILLA" not in cart_skus:
            suggestions.append("SKU_VANILLA")
            
    return suggestions


