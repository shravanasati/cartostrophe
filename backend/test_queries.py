import httpx
import json

BASE_URL = "http://127.0.0.1:8000"

QUERIES = [
    "organic diapers for 6 month baby under 200 AED",
    "حفاضات عضوية لطفل عمره 6 شهور",
    "teething toys for infants safe and BPA free",
    "هدية لصديقة عندها طفل حديث الولادة",
    "baby stroller lightweight travel friendly",
    "لعبة آمنة للتسنين للرضع",
    "gift for newborn baby girl under 150 AED",
    "عربة أطفال خفيفة للسفر",

    "need something for my baby skin very sensitive keeps getting rash pls help",
    "my kid 6 months biting everything what should I buy",
    "cheap but good diapers not causing irritation",
    "friend just had baby what thoughtful gift not too expensive",
    "need حفاضات organic for baby under 200",
    "gift for newborn something مميز",
    "baby stroller خفيف للسفر",

    "diapers under 150 AED for newborn organic",
    "stroller under 300 AED lightweight foldable",
    "toys for 1 year old safe non toxic under 100",

    "something good for baby",
    "best product for kids",
    "what should I buy",

    "premium high quality diapers under 50 AED",
    "organic luxury gift but very cheap",
    "best stroller lightweight but also very heavy duty rugged",

    "best laptop for coding",
    "medicine for baby fever",
    "how to treat infection in infants",

    "diapers that are edible and taste good",
    "toy that guarantees baby will never cry",
    "100% chemical free plastic toy",

    "",
    "asdasd qeusefwe",
    "👶🪀 need something good"
]

def test_endpoints():
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        for query in QUERIES:
            print(f"\n{'='*50}")
            print(f"QUERY: {query}")
            print(f"{'='*50}")

            # Test NLU Endpoint
            print("\n[NLU Extraction]")
            try:
                nlu_resp = client.post("/nlu", json={"prompt": query})
                nlu_resp.raise_for_status()
                print(json.dumps(nlu_resp.json(), indent=2))
            except Exception as e:
                print(f"Error calling /nlu: {e}")

            # Test Search Endpoint
            print("\n[Search Results]")
            try:
                search_resp = client.post("/search", json={"prompt": query, "limit": 5})
                search_resp.raise_for_status()
                results = search_resp.json()
                
                # Assume results is a dict with a 'products' or 'matches' list based on typical SelectionResult
                # Printing raw JSON for completeness
                print(json.dumps(results, indent=2))
            except Exception as e:
                print(f"Error calling /search: {e}")

            input()

if __name__ == "__main__":
    test_endpoints()
