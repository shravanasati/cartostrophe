import logging
import os
from typing import Any, Literal

from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from langchain_openai import ChatOpenAI

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL_NAME = "openai/gpt-oss-120b"

logger = logging.getLogger("cartostrophe")

Category = Literal["gear", "diapers", "feeding", "skincare", "toys"]

TargetCustomer = Literal["baby", "mother"]

Attribute = Literal[
    "motor-skills",
    "hand-woven",
    "traditional",
    "multi-purpose",
    "active-play",
    "educational",
    "best-seller",
    "soft-loops",
    "sensitive",
    "daily",
    "advanced",
    "transport-bag",
    "classic",
    "booster-seat",
    "side-impact-protection",
    "multi-sensory",
    "gentle",
    "portable",
    "tummy-time",
    "overnight",
    "foldable",
    "multiple-pockets",
    "dermatologically-tested",
    "spill-proof",
    "removable-tray",
    "100%-pure",
    "zinc-oxide",
    "fragrance-free",
    "car-safety",
    "natural-scent",
    "dentist-recommended",
    "anti-colic-valve",
    "easy-change",
    "mesh-feeder",
    "fun-patterns",
    "easy-tear-sides",
    "iconic",
    "premium",
    "organic",
    "hypoallergenic",
    "multi-use",
    "outdoor-friendly",
    "diaper-change-hero",
    "almond-oil",
    "leak-barrier",
    "quick-cycle",
    "4-in-1",
    "wheels",
    "rash-treatment",
    "USB-rechargeable",
    "lights-music",
    "chameleon-stretch",
    "safe-size",
    "pH-balanced",
    "reliable",
    "blender",
    "easy-clean",
    "large-capacity",
    "multi-position",
    "dermatologist-tested",
    "ultra-dry",
    "lightweight",
    "waterproof",
    "breathable",
    "cabin-size",
    "flushing-sound",
    "steamer",
    "bedtime",
    "all-in-one",
    "bath-toy",
    "self-feeding",
    "counting",
    "umbilical-cord-cut",
    "cotton-soft",
    "cheap",
    "fruit-veggie-safe",
    "high-absorbency",
    "insulated-pockets",
    "tear-free",
    "natural-ingredients",
    "anti-colic",
    "paraben-free",
    "eco-friendly",
    "no-more-tears",
    "stylish",
    "rash-free",
    "no-mineral-oil",
    "sensory-play",
    "dishwasher-safe",
    "calendula-extract",
    "durable",
    "building-blocks",
    "quick-dry",
    "breastfeeding-support",
    "mild",
    "pre-sterilized",
    "safety-first",
    "adjustable-height",
    "barrier-cream",
    "vent-system",
    "shatter-resistant",
    "food-grade",
    "non-greasy",
    "sturdy",
    "cozy",
    "soap-free",
    "hard-pages",
    "soft-silicone",
    "breathable-backsheet",
    "essential",
    "stacking",
    "micellar-water",
    "color-recognition",
    "natural-rubber",
    "everyday",
    "leak-proof",
    "stroller-toy",
    "swim-diaper",
    "wooden",
    "sorting-toy",
    "active-baby",
    "clinically-proven",
    "hand-painted",
    "convertible",
    "quick-cleanse",
    "open-ended-play",
    "swim-ready",
    "travel-friendly",
    "interactive",
    "glycerin-enriched",
    "daily-use",
    "chemical-free",
    "fine-motor-skills",
    "soft",
    "sensitive-skin",
    "high-tolerance",
    "vegan-leather",
    "teether-included",
    "absorbent-core",
    "flexible-fit",
    "disposable",
    "standard-neck",
    "eczema-prone",
    "bpa-free",
    "budget",
    "creative",
    "soothing",
    "double-pump",
    "cuddle-toy",
    "compact",
    "tray-included",
    "non-swelling",
    "musical",
    "outdoor-toy",
    "ergonomic",
    "stretchable",
    "pool-safe",
    "elastic-waist",
    "comfortable",
    "washable",
    "soft-plush",
    "realistic",
    "easy-install",
    "sterilization",
    "diaper-changer",
    "teething",
    "natural-latch",
    "fun-design",
    "toilet-training",
    "natural-oats",
]

class ProductFilter(BaseModel):
    category: Category | None = Field(default=None, description="Product category")
    min_age: int | None = Field(
        default=0, description="Minimum age in months (null for mothers)"
    )
    max_age: int | None = Field(
        default=1200, description="Maximum age in months (null for mothers)"
    )
    target_customer: TargetCustomer | None = Field(
        default=None, description="Target customer type"
    )
    attributes: list[Attribute] | None = Field(
        default=None, description="Required attributes"
    )
    attributes_strict: bool = Field(
        default=False,
        description="If true, all attributes must be present on the product",
    )
    price_min: float | None = Field(default=None, description="Minimum price")
    price_max: float | None = Field(default=None, description="Maximum price")
    rating_min: float | None = Field(
        default=None, ge=0, le=5, description="Minimum rating (0-5)"
    )
    rating_max: float | None = Field(
        default=None, ge=0, le=5, description="Maximum rating (0-5)"
    )


SYSTEM_PROMPT = """You extract structured filters from user prompts to query a product vector database.
Return only fields that are explicitly stated or strongly implied. Use null when unknown.
Use the exact enum value for `category`, `target_customer`, and `attributes`.
Use ages in months for `min_age` and `max_age`. For mothers, set both to null.
Keep `attributes` as short, lowercase strings from the allowed list.
If an attribute is not in the allowed list, omit it. If none match, set `attributes` to null.
If the user implies price tier, set a price range: "premium" => price_min 100.0, "budget" or "cheap" => price_max 60.0.
Set `attributes_strict` to true only when the user explicitly requires attributes ("must", "only", "required", "no X").
Do not add any fields that are not in the schema.

Few-shot examples:

User: "Need eco-friendly diapers for 0-6 months, under 130."
Assistant (structured): {
    "category": "diapers",
    "min_age": 0,
    "max_age": 6,
    "target_customer": "baby",
    "price_max": 130.0,
    "attributes": ["eco-friendly"],
    "attributes_strict": false
}

User: "Looking for a premium stroller, lightweight and travel-friendly, rating 4.5+."
Assistant (structured): {
    "category": "gear",
    "attributes": ["premium", "lightweight", "travel-friendly"],
    "attributes_strict": false,
    "price_min": 100.0,
    "rating_min": 4.5
}

User: "Toys for 6-24 months, budget, maybe stacking cups."
Assistant (structured): {
    "category": "toys",
    "min_age": 6,
    "max_age": 24,
    "target_customer": "baby",
    "attributes": ["budget", "stacking"],
    "attributes_strict": false,
    "price_max": 60.0
}

User: "Breast pump for mothers, premium and portable."
Assistant (structured): {
    "category": "feeding",
    "target_customer": "mother",
    "min_age": null,
    "max_age": null,
    "attributes": ["premium", "portable"],
    "attributes_strict": false,
    "price_min": 100.0
}

User: "Cheap baby shampoo for sensitive skin."
Assistant (structured): {
    "category": "skincare",
    "target_customer": "baby",
    "attributes": ["sensitive-skin", "cheap"],
    "attributes_strict": false,
    "price_max": 60.0
}

User: "Newborn diapers, gentle and fragrance-free."
Assistant (structured): {
    "category": "diapers",
    "min_age": 0,
    "max_age": 3,
    "target_customer": "baby",
    "attributes": ["gentle", "fragrance-free"],
    "attributes_strict": false
}

User: "Teething toys for a 12-18 month toddler, dishwasher safe."
Assistant (structured): {
    "category": "toys",
    "min_age": 12,
    "max_age": 18,
    "target_customer": "baby",
    "attributes": ["teething", "dishwasher-safe"],
    "attributes_strict": false
}

User: "Only organic, fragrance-free skincare for a newborn."
Assistant (structured): {
    "category": "skincare",
    "min_age": 0,
    "max_age": 3,
    "target_customer": "baby",
    "attributes": ["organic", "fragrance-free"],
    "attributes_strict": true
}
"""


class NLUEngine:
    def __init__(self) -> None:
        api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Missing GROQ_API_KEY or OPENAI_API_KEY")

        model = ChatOpenAI(
            model=GROQ_MODEL_NAME,
            base_url=GROQ_BASE_URL,
            api_key=api_key,
            temperature=0,
        )
        self._agent = create_agent(
            model=model,
            tools=[],
            response_format=ProviderStrategy(ProductFilter),
            system_prompt=SYSTEM_PROMPT,
        )

    def extract(self, prompt: str) -> ProductFilter:
        try:
            result: dict[str, Any] = self._agent.invoke(
                {"messages": [{"role": "user", "content": prompt}]}
            )
            return result["structured_response"]
        except ValueError as exc:
            logger.warning("validation failed, retrying once with error details")
            previous_output = str(exc)
            retry_messages = [
                {"role": "user", "content": prompt},
                {
                    "role": "system",
                    "content": (
                        "Validation error from previous attempt:\n"
                        f"{exc}\n\nPrevious output (verbatim):\n"
                        f"{previous_output}\n\nFix the output and return valid JSON only."
                    ),
                },
            ]
            result: dict[str, Any] = self._agent.invoke(
                {"messages": retry_messages}
            )
            return result["structured_response"]
