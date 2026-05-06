"""Realistic mock data for GoogleMart Virtual Chef."""

PRODUCTS = {
    "SKU_MILK": {
        "name": "Full Cream Milk 1L",
        "price": 2.50,
        "macros": {"protein": 3.4, "carbs": 4.8, "fat": 3.4},
        "allergens": ["dairy"],
        "image_keyword": "milk",
    },
    "SKU_BREAD": {
        "name": "Wholemeal Bread Loaf 700g",
        "price": 3.50,
        "macros": {"protein": 8.5, "carbs": 42, "fat": 2},
        "allergens": ["gluten"],
        "image_keyword": "bread",
    },
    "SKU_EGGS": {
        "name": "Large Free Range Eggs 12 Pack",
        "price": 7.00,
        "macros": {"protein": 12.6, "carbs": 0.7, "fat": 9.5},
        "allergens": ["eggs"],
        "image_keyword": "eggs",
    },
    "SKU_RICE": {
        "name": "White Basmati Rice 1kg",
        "price": 2.50,
        "macros": {"protein": 8, "carbs": 78, "fat": 0.5},
        "allergens": [],
        "image_keyword": "rice",
    },
    "SKU_APPLES": {
        "name": "Pink Lady Apples 1kg",
        "price": 5.00,
        "macros": {"protein": 0.3, "carbs": 14, "fat": 0.2},
        "allergens": [],
        "image_keyword": "apples",
    },
    "SKU_BANANAS": {
        "name": "Cavendish Bananas 1kg",
        "price": 4.00,
        "macros": {"protein": 1.1, "carbs": 23, "fat": 0.3},
        "allergens": [],
        "image_keyword": "bananas",
    },
    "SKU_CHICKEN": {
        "name": "Fresh Chicken Breast Fillets 1kg",
        "price": 13.50,
        "macros": {"protein": 31, "carbs": 0, "fat": 3.6},
        "allergens": [],
        "image_keyword": "chicken,breast",
    },
    "SKU_BEEF": {
        "name": "Premium Beef Mince 500g",
        "price": 12.00,
        "macros": {"protein": 22, "carbs": 0, "fat": 15},
        "allergens": [],
        "image_keyword": "beef,mince",
    },
    "SKU_CHEESE": {
        "name": "Tasty Cheddar Cheese 500g",
        "price": 10.00,
        "macros": {"protein": 25, "carbs": 1, "fat": 33},
        "allergens": ["dairy"],
        "image_keyword": "cheese",
    },
    "SKU_PASTA": {
        "name": "Penne Pasta 500g",
        "price": 2.50,
        "macros": {"protein": 12, "carbs": 71, "fat": 1.5},
        "allergens": ["gluten"],
        "image_keyword": "pasta",
    },
    "SKU_GARLIC": {
        "name": "Garlic Bulb",
        "price": 1.00,
        "macros": {},
        "allergens": [],
        "image_keyword": "garlic",
    },
    "SKU_CREAM": {
        "name": "Heavy Cream 300ml",
        "price": 3.50,
        "macros": {"protein": 2.1, "carbs": 2.8, "fat": 35},
        "allergens": ["dairy"],
        "image_keyword": "cream",
    },
}

RECIPES = [
    {
        "name": "Creamy Garlic Chicken Pasta",
        "ingredients": [
            "SKU_CHICKEN",
            "SKU_PASTA",
            "SKU_GARLIC",
            "SKU_CREAM",
        ],
        "optional_ingredients": ["SKU_CHEESE"],
        "instructions": "Cook pasta. Sear chicken. Add garlic and cream. Mix with pasta.",
    },
    {
        "name": "Classic Bolognese",
        "ingredients": ["SKU_BEEF", "SKU_PASTA", "SKU_GARLIC"],
        "optional_ingredients": ["SKU_CHEESE"],
        "instructions": "Brown beef with garlic. Simmer. Serve over pasta.",
    },
]

MOCK_CART = [
    "SKU_CHICKEN",
    "SKU_PASTA",
    "SKU_GARLIC",
    "SKU_CREAM",
]
