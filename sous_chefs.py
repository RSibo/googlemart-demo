"""Sous Chefs for GoogleMart."""

from google3.labs.language.genai.agents.googlemart.mock_data import PRODUCTS, RECIPES

def meal_planner(cart_items: list[str]) -> list[dict]:
    """Identifies recipes based on basket contents."""
    available_skus = set(cart_items)
    matching_recipes = []
    
    for recipe in RECIPES:
        recipe_skus = set(recipe["ingredients"])
        # If we have all core ingredients, or at least most of them
        # For simplicity, let's say we match if we have at least 3 ingredients
        common = available_skus.intersection(recipe_skus)
        if len(common) >= 3:
            matching_recipes.append(recipe)
            
    return matching_recipes

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

def sommelier(product_sku: str) -> list[str]:
    """Handles flavor pairings (wines, sides)."""
    suggestions = []
    if product_sku == "SKU_STEAK":
        suggestions.extend(["SKU_WINE_RED", "SKU_ROSEMARY", "SKU_BUTTER"])
    elif product_sku == "SKU_SALMON":
        suggestions.extend(["SKU_ASPARAGUS"])
        
    return suggestions
