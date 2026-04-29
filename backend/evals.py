import json
import httpx
import numpy as np
from typing import List, Dict, Any
import logging

BASE_URL = "http://127.0.0.1:8000"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("evals")

class Evals:
    def __init__(self, golden_path: str = "./golden_dataset.json", cache_path: str = "./eval_cache.json"):
        with open(golden_path, "r", encoding="utf-8") as f:
            self.golden_data = json.load(f)
        self.cache_path = cache_path
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        try:
            with open(self.cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_cache(self):
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, indent=2, ensure_ascii=False)

    def calculate_recall_at_k(self, relevant_ids: List[int], retrieved_ids: List[int], k: int) -> float:
        if not relevant_ids:
            return 1.0
        retrieved_k = retrieved_ids[:k]
        relevant_set = set(relevant_ids)
        hits = len([idx for idx in retrieved_k if idx in relevant_set])
        return hits / len(relevant_ids)

    def calculate_ndcg_at_k(self, relevant_ids: List[int], retrieved_ids: List[int], k: int) -> float:
        relevant_set = set(relevant_ids)
        dcg = 0.0
        for i, idx in enumerate(retrieved_ids[:k]):
            if idx in relevant_set:
                dcg += 1.0 / np.log2(i + 2)
        
        idcg = 0.0
        for i in range(min(len(relevant_ids), k)):
            idcg += 1.0 / np.log2(i + 2)
            
        return dcg / idcg if idcg > 0 else 0.0

    def evaluate_behavior(self, expected: Dict[str, Any], actual: Dict[str, Any]) -> Dict[str, bool]:
        results = {
            "category_match": actual.get("category") == expected.get("expected_category") if expected.get("expected_category") else True,
            "target_customer_match": actual.get("target_customer") == expected.get("expected_target_customer") if expected.get("expected_target_customer") else True,
            "price_max_match": (actual.get("price_max") or float('inf')) <= (expected.get("expected_price_max") or float('inf')) if expected.get("expected_price_max") else True,
            "min_age_match": (actual.get("min_age") or 0) >= (expected.get("expected_min_age") or 0) if expected.get("expected_min_age") else True,
            "attributes_match": all(attr in actual.get("attributes", []) for attr in expected.get("expected_attributes", [])) if expected.get("expected_attributes") else True
        }
        return results

    async def run_evals(self):
        metrics = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            for i, entry in enumerate(self.golden_data):
                query = entry["query"]
                expected_retrieval = entry["retrieval"]["relevant_product_ids"]
                expected_behavior = entry["behavior"]

                # Check cache first
                if query in self.cache:
                    logger.info(f"Using cached result for query: {query}")
                    cached_data = self.cache[query]
                    actual_behavior = cached_data["nlu"]
                    search_data = cached_data["search"]
                else:
                    # Rate limiting: 3 queries per minute = 20 seconds per query
                    # Only wait if we are actually making a network call
                    if len(self.cache) > 0 or i > 0:
                        logger.info(f"Rate limiting: waiting 20 seconds before query {i+1}/{len(self.golden_data)}...")
                        await asyncio.sleep(20)

                    try:
                        # 1. Test NLU
                        nlu_resp = await client.post(f"{BASE_URL}/nlu", json={"prompt": query})
                        nlu_resp.raise_for_status()
                        actual_behavior = nlu_resp.json()

                        # 2. Test Retrieval
                        search_resp = await client.post(f"{BASE_URL}/search", json={"prompt": query, "limit": 10})
                        search_resp.raise_for_status()
                        search_data = search_resp.json()

                        # Save to cache
                        self.cache[query] = {
                            "nlu": actual_behavior,
                            "search": search_data
                        }
                        self._save_cache()

                    except Exception as e:
                        logger.error(f"Error evaluating query '{query}': {e}")
                        metrics.append({
                            "query": query,
                            "success": False,
                            "error": str(e)
                        })
                        continue

                try:
                    behavior_results = self.evaluate_behavior(expected_behavior, actual_behavior)
                    
                    # API returns IDs in a top-level "ids" key, not "products"
                    retrieved_ids = search_data.get("ids", [])

                    k = 3
                    r_at_k = self.calculate_recall_at_k(expected_retrieval, retrieved_ids, k)
                    ndcg = self.calculate_ndcg_at_k(expected_retrieval, retrieved_ids, k)

                    metrics.append({
                        "query": query,
                        "recall@3": r_at_k,
                        "ndcg@3": ndcg,
                        "behavior": behavior_results,
                        "success": True
                    })
                except Exception as e:
                    logger.error(f"Error evaluating query '{query}': {e}")
                    metrics.append({
                        "query": query,
                        "success": False,
                        "error": str(e)
                    })

        self.print_summary(metrics)

    def print_summary(self, metrics: List[Dict[str, Any]]):
        successful = [m for m in metrics if m["success"]]
        if not successful:
            print("No successful evaluations.")
            return

        avg_r = np.mean([m["recall@3"] for m in successful])
        avg_ndcg = np.mean([m["ndcg@3"] for m in successful])

        print("\n--- Evaluation Summary ---")
        print(f"Total Queries: {len(metrics)}")
        print(f"Successful: {len(successful)}")
        print(f"Average Recall@3: {avg_r:.4f}")
        print(f"Average NDCG@3: {avg_ndcg:.4f}")
        
        print("\n--- Behavioral Heuristics ---")
        for key in successful[0]["behavior"].keys():
            match_rate = np.mean([m["behavior"][key] for m in successful])
            print(f"{key}: {match_rate:.2%}")

if __name__ == "__main__":
    import asyncio
    evaluator = Evals()
    asyncio.run(evaluator.run_evals())
