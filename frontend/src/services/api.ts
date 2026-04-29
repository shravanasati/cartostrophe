export interface Product {
  id: number;
  name_en: string;
  name_ar: string;
  category: string;
  price: number;
  currency: string;
  min_age: number | null;
  max_age: number | null;
  target_customer: string | null;
  attributes: string[];
  description_en: string;
  description_ar: string;
  rating: number;
  review_count: number;
}

export interface SelectionResult {
  ids: number[];
  reasoning_en: string;
  reasoning_ar: string;
}

const API_URL = import.meta.env.VITE_API_URL;

export async function fetchProducts(): Promise<Product[]> {
  try {
    const response = await fetch(`${API_URL}/products`);
    if (!response.ok) {
      throw new Error(`Failed to fetch products: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching products:", error);
    return [];
  }
}

export async function searchProducts(prompt: string, limit: number = 20): Promise<SelectionResult | null> {
  try {
    const response = await fetch(`${API_URL}/search`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ prompt, limit }),
    });
    if (!response.ok) {
      throw new Error(`Failed to search products: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Error searching products:", error);
    return null;
  }
}
