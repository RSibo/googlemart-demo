export interface Product {
  sku: string;
  name: string;
  price: number;
  macros: {
    protein?: number;
    carbs?: number;
    fat?: number;
  };
  allergens: string[];
  image_keyword: string;
  image_url?: string;
}

export interface CartItem extends Product {
  quantity: number;
}

export interface ChefSettings {
  accessToken: string;
  projectId: string;
  location: string;
  modelId: string;
  voice: string;
  avatar: string;
}

export interface ChatMessage {
  role: 'user' | 'chef';
  content: string;
  id: string;
  suggestion?: string; // SKU
  ui?: {
    component: string;
    props: any;
  };
}

export interface Recipe {
  name: string;
  ingredients: string[];
  instructions: string;
  prep_time?: string;
}
