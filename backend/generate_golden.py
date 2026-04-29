import json
from typing import TypedDict, List, Optional

# Mocking the models for generation script
class Behavior(TypedDict, total=False):
    expected_category: Optional[str]
    expected_target_customer: Optional[str]
    expected_price_min: Optional[float]
    expected_price_max: Optional[float]
    expected_min_age: Optional[int]
    expected_max_age: Optional[int]
    expected_attributes: Optional[List[str]]
    expected_attributes_strict: Optional[bool]
    expected_rating_min: Optional[float]

class Retrieval(TypedDict):
    relevant_product_ids: List[int]

class GoldenEntry(TypedDict):
    query: str
    retrieval: Retrieval
    behavior: Behavior

def generate_golden_dataset():
    # Load dataset to verify IDs and categories
    with open("./dataset.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)

    # Helper to find products by keywords or filter
    def find_products(category=None, max_price=None, min_age=None, max_age=None, attributes=None):
        ids = []
        for p in dataset:
            if category and p.get("category") != category: continue
            if max_price and p.get("price") is not None and p.get("price") > max_price: continue
            
            p_min_age = p.get("min_age")
            p_max_age = p.get("max_age")
            
            if min_age is not None:
                if p_max_age is None or p_max_age < min_age: continue
            if max_age is not None:
                if p_min_age is None or p_min_age > max_age: continue
                
            if attributes:
                if not all(attr in p.get("attributes", []) for attr in attributes):
                    continue
            ids.append(p["id"])
        return ids

    golden_dataset: List[GoldenEntry] = [
        {
            "query": "organic diapers for 6 month baby under 200 AED",
            "retrieval": {
                "relevant_product_ids": find_products(category="diapers", max_price=200, min_age=6, max_age=6, attributes=["organic"])
            },
            "behavior": {
                "expected_category": "diapers",
                "expected_price_max": 200.0,
                "expected_min_age": 6,
                "expected_max_age": 6,
                "expected_target_customer": "baby",
                "expected_attributes": ["organic"]
            }
        },
        {
            "query": "baby stroller lightweight travel friendly",
            "retrieval": {
                "relevant_product_ids": find_products(category="gear", attributes=["lightweight", "travel-friendly"])
            },
            "behavior": {
                "expected_category": "gear",
                "expected_attributes": ["lightweight", "travel-friendly"],
                "expected_target_customer": "baby"
            }
        },
        {
            "query": "teething toys for infants safe and BPA free",
            "retrieval": {
                "relevant_product_ids": find_products(category="toys", attributes=["teething", "bpa-free"])
            },
            "behavior": {
                "expected_category": "toys",
                "expected_attributes": ["teething", "bpa-free"],
                "expected_target_customer": "baby"
            }
        },
        {
            "query": "cheap but good diapers not causing irritation",
            "retrieval": {
                "relevant_product_ids": find_products(category="diapers", max_price=60, attributes=["sensitive-skin"])
            },
            "behavior": {
                "expected_category": "diapers",
                "expected_price_max": 60.0,
                "expected_attributes": ["cheap", "sensitive-skin"]
            }
        },
        {
            "query": "premium high quality diapers under 150 AED",
            "retrieval": {
                "relevant_product_ids": find_products(category="diapers", max_price=150, attributes=["premium"])
            },
            "behavior": {
                "expected_category": "diapers",
                "expected_price_max": 150.0,
                "expected_attributes": ["premium"]
            }
        },
        {
            "query": "gift for newborn baby girl under 150 AED",
            "retrieval": {
                "relevant_product_ids": find_products(max_price=150, min_age=0, max_age=3)
            },
            "behavior": {
                "expected_price_max": 150.0,
                "expected_min_age": 0,
                "expected_max_age": 3,
                "expected_target_customer": "baby"
            }
        },
        {
            "query": "organic luxury gift but very cheap",
            "retrieval": {
                "relevant_product_ids": find_products(max_price=60, attributes=["organic", "premium"])
            },
            "behavior": {
                "expected_attributes": ["organic", "premium", "cheap"],
                "expected_price_max": 60.0
            }
        },
        {
            "query": "حفاضات عضوية لطفل عمره 6 شهور",
            "retrieval": {
                "relevant_product_ids": find_products(category="diapers", attributes=["organic"], min_age=6, max_age=6)
            },
            "behavior": {
                "expected_category": "diapers",
                "expected_attributes": ["organic"],
                "expected_min_age": 6,
                "expected_max_age": 6
            }
        },
        {
            "query": "هدية لصديقة عندها طفل حديث الولادة",
            "retrieval": {
                "relevant_product_ids": find_products(min_age=0, max_age=3)
            },
            "behavior": {
                "expected_min_age": 0,
                "expected_max_age": 3,
                "expected_target_customer": "baby"
            }
        },
        {
            "query": "لعبة آمنة للتسنين للرضع",
            "retrieval": {
                "relevant_product_ids": find_products(category="toys", attributes=["teething"])
            },
            "behavior": {
                "expected_category": "toys",
                "expected_attributes": ["teething"],
                "expected_target_customer": "baby"
            }
        },
        {
            "query": "عربة أطفال خفيفة للسفر",
            "retrieval": {
                "relevant_product_ids": find_products(category="gear", attributes=["lightweight", "travel-friendly"])
            },
            "behavior": {
                "expected_category": "gear",
                "expected_attributes": ["lightweight", "travel-friendly"]
            }
        },
        {
            "query": "need something for my baby skin very sensitive keeps getting rash pls help",
            "retrieval": {
                "relevant_product_ids": find_products(category="skincare", attributes=["sensitive-skin", "rash-treatment"])
            },
            "behavior": {
                "expected_category": "skincare",
                "expected_attributes": ["sensitive-skin", "rash-treatment"]
            }
        },
        {
            "query": "my kid 6 months biting everything what should I buy",
            "retrieval": {
                "relevant_product_ids": find_products(category="toys", attributes=["teething"], min_age=6, max_age=6)
            },
            "behavior": {
                "expected_category": "toys",
                "expected_attributes": ["teething"],
                "expected_min_age": 6,
                "expected_max_age": 6
            }
        },
        {
            "query": "stroller under 300 AED lightweight foldable",
            "retrieval": {
                "relevant_product_ids": find_products(category="gear", max_price=300, attributes=["lightweight", "foldable"])
            },
            "behavior": {
                "expected_category": "gear",
                "expected_price_max": 300.0,
                "expected_attributes": ["lightweight", "foldable"]
            }
        }
    ]

    with open("./golden_dataset.json", "w", encoding="utf-8") as f:
        json.dump(golden_dataset, f, indent=2, ensure_ascii=False)
    
    print(f"Generated golden dataset with {len(golden_dataset)} entries.")

if __name__ == "__main__":
    generate_golden_dataset()
