"""Realistic mock data for GoogleMart Virtual Chef."""

PRODUCTS = {
    "SKU_MILK_FULL": {
        "name": "Woolworths Full Cream Milk 2L",
        "price": 3.10,
        "macros": {"protein": 3.4, "carbs": 4.8, "fat": 3.4},
        "allergens": ["dairy"],
        "image_keyword": "milk,bottle,full-cream",
        "image_url": "https://cdn0.woolworths.media/content/wowproductimages/large/139140.jpg",
    },
    "SKU_BREAD_WHITE": {
        "name": "Woolworths White Sandwich Bread 700g",
        "price": 2.70,
        "macros": {"protein": 7.5, "carbs": 45, "fat": 1.5},
        "allergens": ["gluten"],
        "image_keyword": "white,bread,loaf",
        "image_url": "https://cdn0.woolworths.media/content/wowproductimages/large/114400.jpg",
    },
    "SKU_EGGS_FREE": {
        "name": "Woolworths Free Range Large Eggs 12pk 700g",
        "price": 5.50,
        "macros": {"protein": 12.6, "carbs": 0.7, "fat": 9.5},
        "allergens": ["eggs"],
        "image_keyword": "eggs,carton",
        "image_url": "https://cdn0.woolworths.media/content/wowproductimages/large/733854.jpg",
    },
    "SKU_CHICKEN_BREAST": {
        "name": "Woolworths Chicken Breast Fillet 1kg",
        "price": 14.50,
        "macros": {"protein": 31, "carbs": 0, "fat": 3.6},
        "allergens": [],
        "image_keyword": "chicken,breast,raw",
        "image_url": "https://cdn0.woolworths.media/content/wowproductimages/large/243452.jpg",
    },
    "SKU_BANANAS_KG": {
        "name": "Bananas 1kg",
        "price": 4.50,
        "macros": {"protein": 1.1, "carbs": 23, "fat": 0.3},
        "allergens": [],
        "image_keyword": "bananas,bunch",
        "image_url": "https://cdn0.woolworths.media/content/wowproductimages/large/133211.jpg",
    },
    "SKU_AVOCADO_EACH": {
        "name": "Hass Avocado Each",
        "price": 1.50,
        "macros": {"protein": 2, "carbs": 8.5, "fat": 15},
        "allergens": [],
        "image_keyword": "avocado,hass",
        "image_url": "https://cdn0.woolworths.media/content/wowproductimages/large/161825.jpg",
    },
    "SKU_MINCE_BEEF": {
        "name": "Woolworths Beef Mince Typical Fat 500g",
        "price": 8.50,
        "macros": {"protein": 20, "carbs": 0, "fat": 15},
        "allergens": [],
        "image_keyword": "beef,mince,raw",
        "image_url": "https://cdn0.woolworths.media/content/wowproductimages/large/486791.jpg",
    },
    "SKU_PASTA_PENNE": {
        "name": "Woolworths Penne Pasta 500g",
        "price": 1.30,
        "macros": {"protein": 12, "carbs": 71, "fat": 1.5},
        "allergens": ["gluten"],
        "image_keyword": "penne,pasta,dry",
        "image_url": "https://cdn0.woolworths.media/content/wowproductimages/large/138139.jpg",
    },
    "SKU_TOMATO_SAUCE": {
        "name": "Woolworths Tomato Pasta Sauce 500g",
        "price": 2.20,
        "macros": {"protein": 1.5, "carbs": 7, "fat": 0.5},
        "allergens": [],
        "image_keyword": "tomato,sauce,jar",
        "image_url": "https://cdn0.woolworths.media/content/wowproductimages/large/140411.jpg",
    },
    "SKU_CHEESE_BLOCK": {
        "name": "Woolworths Tasty Cheese Block 500g",
        "price": 7.50,
        "macros": {"protein": 25, "carbs": 1, "fat": 33},
        "allergens": ["dairy"],
        "image_keyword": "cheddar,cheese,block",
        "image_url": "https://cdn0.woolworths.media/content/wowproductimages/large/125134.jpg",
    },
    "SKU_APPLES_PINK": {
        "name": "Pink Lady Apples 1kg Pack",
        "price": 5.50,
        "macros": {"protein": 0.3, "carbs": 14, "fat": 0.2},
        "allergens": [],
        "image_keyword": "apples,pink-lady",
        "image_url": "https://cdn0.woolworths.media/content/wowproductimages/large/132488.jpg",
    },
    "SKU_GARLIC_EACH": {
        "name": "Garlic Loose Each",
        "price": 0.80,
        "macros": {},
        "allergens": [],
        "image_keyword": "garlic,bulb",
        "image_url": "https://cdn0.woolworths.media/content/wowproductimages/large/133246.jpg",
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
