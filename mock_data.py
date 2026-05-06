"""Mock data for GoogleMart Virtual Chef."""

PRODUCTS = {
    "SKU_CHICKEN": {
        "name": "Fresh Chicken Breast",
        "price": 12.00,
        "macros": {"protein": 31, "carbs": 0, "fat": 3.6},
        "allergens": [],
        "tags": ["poultry", "high-protein"],
    },
    "SKU_SPINACH": {
        "name": "Baby Spinach 200g",
        "price": 4.00,
        "macros": {"protein": 2.9, "carbs": 3.6, "fat": 0.4},
        "allergens": [],
        "tags": ["vegetable", "greens"],
    },
    "SKU_CREAM": {
        "name": "Heavy Cream 300ml",
        "price": 3.50,
        "macros": {"protein": 2.1, "carbs": 2.8, "fat": 35},
        "allergens": ["dairy"],
        "tags": ["dairy"],
    },
    "SKU_PASTA": {
        "name": "Penne Pasta 500g",
        "price": 2.50,
        "macros": {"protein": 12, "carbs": 71, "fat": 1.5},
        "allergens": ["gluten"],
        "tags": ["pantry", "carbs"],
    },
    "SKU_GARLIC": {
        "name": "Garlic Bulb",
        "price": 1.00,
        "macros": {"protein": 6.4, "carbs": 33, "fat": 0.5},
        "allergens": [],
        "tags": ["produce", "flavor"],
    },
    "SKU_BEEF": {
        "name": "Premium Ground Beef 500g",
        "price": 10.00,
        "macros": {"protein": 22, "carbs": 0, "fat": 15},
        "allergens": [],
        "tags": ["meat", "beef", "high-protein"],
    },
    "SKU_STEAK": {
        "name": "Ribeye Steak 300g",
        "price": 25.00,
        "macros": {"protein": 25, "carbs": 0, "fat": 22},
        "allergens": [],
        "tags": ["meat", "steak", "luxury"],
    },
    "SKU_PARMESAN": {
        "name": "Parmesan Cheese 100g",
        "price": 5.00,
        "macros": {"protein": 35, "carbs": 4.1, "fat": 26},
        "allergens": ["dairy"],
        "tags": ["dairy", "cheese"],
    },
    "SKU_WINE_RED": {
        "name": "Shiraz Red Wine",
        "price": 20.00,
        "macros": {},
        "allergens": [],
        "tags": ["alcohol", "wine", "red-wine"],
    },
    "SKU_ROSEMARY": {
        "name": "Fresh Rosemary Branch",
        "price": 2.00,
        "macros": {},
        "allergens": [],
        "tags": ["produce", "herb"],
    },
    "SKU_BUTTER": {
        "name": "Unsalted Butter 250g",
        "price": 4.00,
        "macros": {"protein": 0.9, "carbs": 0.1, "fat": 81},
        "allergens": ["dairy"],
        "tags": ["dairy"],
    },
    "SKU_FLOUR": {
        "name": "Plain Flour 1kg",
        "price": 2.00,
        "macros": {"protein": 10, "carbs": 76, "fat": 1},
        "allergens": ["gluten"],
        "tags": ["pantry", "baking"],
    },
    "SKU_SUGAR": {
        "name": "White Sugar 1kg",
        "price": 2.00,
        "macros": {"protein": 0, "carbs": 100, "fat": 0},
        "allergens": [],
        "tags": ["pantry", "baking"],
    },
    "SKU_VANILLA": {
        "name": "Vanilla Extract 50ml",
        "price": 6.00,
        "macros": {},
        "allergens": [],
        "tags": ["pantry", "baking"],
    },
    "SKU_BAKING_POWDER": {
        "name": "Baking Powder 100g",
        "price": 2.00,
        "macros": {},
        "allergens": [],
        "tags": ["pantry", "baking"],
    },
    "SKU_SALMON": {
        "name": "Salmon Fillet 200g",
        "price": 15.00,
        "macros": {"protein": 20, "carbs": 0, "fat": 13},
        "allergens": ["fish"],
        "tags": ["seafood", "fish", "omega-3"],
    },
    "SKU_ASPARAGUS": {
        "name": "Fresh Asparagus Bunch",
        "price": 4.00,
        "macros": {"protein": 2.2, "carbs": 3.9, "fat": 0.1},
        "allergens": [],
        "tags": ["vegetable", "fresh"],
    },
}

RECIPES = [
    {
        "name": "Creamy Garlic Chicken Pasta",
        "ingredients": [
            "SKU_CHICKEN",
            "SKU_SPINACH",
            "SKU_CREAM",
            "SKU_PASTA",
            "SKU_GARLIC",
        ],
        "optional_ingredients": ["SKU_PARMESAN"],
        "instructions": "Cook pasta. Sear chicken. Add garlic, cream, and spinach. Mix with pasta.",
    },
    {
        "name": "Classic Bolognese",
        "ingredients": ["SKU_BEEF", "SKU_PASTA", "SKU_GARLIC"],
        "optional_ingredients": ["SKU_PARMESAN"],
        "instructions": "Brown beef with garlic. Simmer. Serve over pasta.",
        "tags": ["kid-friendly"],
    },
    {
        "name": "Perfect Pan-Seared Ribeye",
        "ingredients": ["SKU_STEAK"],
        "optional_ingredients": ["SKU_BUTTER", "SKU_ROSEMARY"],
        "instructions": "Sear steak in a hot pan. Baste with butter and rosemary.",
    },
]

# Mock cart representing items user has added
MOCK_CART = [
    "SKU_CHICKEN",
    "SKU_SPINACH",
    "SKU_CREAM",
    "SKU_PASTA",
    "SKU_GARLIC",
]
