import csv
import re
from pathlib import Path


# ============================================================
# PAYPILOT AI - SMART PRODUCT RECOMMENDATION ENGINE
# ============================================================
#
# Features:
#   1. Natural language query understanding
#   2. Budget extraction
#   3. Category detection
#   4. Use-case detection
#   5. Feature / requirement detection
#   6. Product keyword matching
#   7. Budget-aware ranking
#   8. Stock-aware ranking
#   9. Product similarity scoring
#   10. Recommendation explanations
#   11. Confidence score
#   12. Top-product selection
#
# No external API key required.
# ============================================================


# ============================================================
# LOAD PRODUCTS
# ============================================================

def load_products():

    csv_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "products.csv"
    )

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Product dataset not found: {csv_path}"
        )

    with open(
        csv_path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        products = []

        for row in reader:

            cleaned = {}

            for key, value in row.items():

                if key is None:
                    continue

                clean_key = str(key).strip().lower()

                clean_value = (
                    str(value).strip()
                    if value is not None
                    else ""
                )

                cleaned[clean_key] = clean_value

            products.append(cleaned)

        return products


# ============================================================
# SAFE HELPERS
# ============================================================

def safe_float(value, default=0.0):

    try:
        if value is None:
            return default

        text = str(value).strip()

        text = (
            text
            .replace("₹", "")
            .replace(",", "")
            .replace("rs.", "")
            .replace("rs", "")
            .replace("inr", "")
            .strip()
        )

        return float(text)

    except (ValueError, TypeError):

        return default


def safe_int(value, default=0):

    try:
        return int(float(str(value).strip()))

    except (ValueError, TypeError):

        return default


def product_text(product):

    fields = [
        product.get("name", ""),
        product.get("category", ""),
        product.get("description", ""),
        product.get("brand", ""),
        product.get("features", ""),
        product.get("tags", ""),
        product.get("keywords", ""),
    ]

    return " ".join(
        str(value)
        for value in fields
        if value
    ).lower()


# ============================================================
# CATEGORY DETECTION
# ============================================================

CATEGORY_KEYWORDS = {

    "laptop": [
        "laptop",
        "notebook",
        "macbook"
    ],

    "headphones": [
        "headphone",
        "headphones",
        "headset",
        "earphone",
        "earphones",
        "earbuds",
        "airpods"
    ],

    "keyboard": [
        "keyboard",
        "mechanical keyboard"
    ],

    "mouse": [
        "mouse",
        "gaming mouse"
    ],

    "monitor": [
        "monitor",
        "display",
        "screen"
    ],

    "smartphone": [
        "phone",
        "smartphone",
        "mobile",
        "iphone",
        "android"
    ],

    "tablet": [
        "tablet",
        "ipad"
    ],

    "speaker": [
        "speaker",
        "speakers",
        "soundbar"
    ],

    "webcam": [
        "webcam",
        "camera",
        "web camera"
    ],

    "charger": [
        "charger",
        "charging adapter",
        "adapter"
    ],

    "powerbank": [
        "powerbank",
        "power bank",
        "portable charger"
    ],

    "television": [
        "television",
        "tv",
        "smart tv"
    ],

    "camera": [
        "camera",
        "dslr",
        "mirrorless"
    ],

    "tablet": [
        "tablet",
        "ipad"
    ],

    "bag": [
        "bag",
        "backpack",
        "laptop bag"
    ]
}


def detect_category(query):

    query = query.lower()

    detected = []

    for category, keywords in CATEGORY_KEYWORDS.items():

        for keyword in keywords:

            if keyword in query:

                detected.append(category)
                break

    return list(dict.fromkeys(detected))


# ============================================================
# USE CASE DETECTION
# ============================================================

USE_CASES = {

    "gaming": [
        "gaming",
        "game",
        "games",
        "gamer",
        "gaming setup",
        "esports",
        "fps",
        "competitive gaming"
    ],

    "coding": [
        "coding",
        "programming",
        "developer",
        "development",
        "software development",
        "python",
        "machine learning",
        "data science",
        "ai",
        "artificial intelligence"
    ],

    "study": [
        "study",
        "studying",
        "student",
        "college",
        "university",
        "education",
        "classes"
    ],

    "online classes": [
        "online class",
        "online classes",
        "zoom",
        "google meet",
        "meetings",
        "virtual class"
    ],

    "office": [
        "office",
        "work",
        "working",
        "work from home",
        "wfh",
        "business",
        "professional"
    ],

    "music": [
        "music",
        "songs",
        "listening",
        "audio",
        "spotify"
    ],

    "travel": [
        "travel",
        "travelling",
        "trip",
        "journey",
        "flight"
    ],

    "fitness": [
        "fitness",
        "gym",
        "workout",
        "exercise"
    ]
}


def detect_use_case(query):

    query = query.lower()

    detected = []

    for use_case, keywords in USE_CASES.items():

        for keyword in keywords:

            if keyword in query:

                detected.append(use_case)
                break

    return list(dict.fromkeys(detected))


# ============================================================
# USE CASE -> PRODUCT RELEVANCE
# ============================================================

USE_CASE_PRODUCTS = {

    "gaming": [
        "laptop",
        "headphones",
        "keyboard",
        "mouse",
        "monitor",
        "controller",
        "speaker"
    ],

    "coding": [
        "laptop",
        "keyboard",
        "mouse",
        "monitor"
    ],

    "study": [
        "laptop",
        "tablet",
        "headphones",
        "keyboard",
        "mouse",
        "webcam"
    ],

    "online classes": [
        "laptop",
        "headphones",
        "webcam",
        "microphone",
        "speaker",
        "tablet"
    ],

    "office": [
        "laptop",
        "keyboard",
        "mouse",
        "monitor",
        "headphones",
        "webcam"
    ],

    "music": [
        "headphones",
        "speaker",
        "earphones",
        "earbuds"
    ],

    "travel": [
        "headphones",
        "earphones",
        "powerbank",
        "charger",
        "bag"
    ],

    "fitness": [
        "smartphone",
        "headphones",
        "smartwatch"
    ]
}


# ============================================================
# FEATURE / REQUIREMENT DETECTION
# ============================================================

FEATURE_SYNONYMS = {

    "wireless": [
        "wireless",
        "cordless"
    ],

    "bluetooth": [
        "bluetooth"
    ],

    "noise cancellation": [
        "noise cancellation",
        "noise cancelling",
        "anc",
        "active noise cancellation"
    ],

    "long battery": [
        "long battery",
        "good battery",
        "great battery",
        "battery life",
        "long lasting battery"
    ],

    "fast charging": [
        "fast charging",
        "quick charging",
        "rapid charging"
    ],

    "lightweight": [
        "lightweight",
        "light weight",
        "light"
    ],

    "portable": [
        "portable",
        "compact",
        "easy to carry"
    ],

    "mechanical": [
        "mechanical",
        "mechanical keys"
    ],

    "rgb": [
        "rgb",
        "rgb lighting"
    ],

    "high refresh rate": [
        "high refresh rate",
        "high refresh",
        "144hz",
        "165hz",
        "240hz",
        "120hz"
    ],

    "ssd": [
        "ssd",
        "nvme",
        "solid state"
    ],

    "large storage": [
        "large storage",
        "more storage",
        "high storage",
        "1tb",
        "2tb",
        "512gb"
    ],

    "good camera": [
        "good camera",
        "great camera",
        "camera quality",
        "better camera"
    ],

    "water resistant": [
        "water resistant",
        "waterproof",
        "ip rating"
    ]
}


def detect_features(query):

    query = query.lower()

    detected = []

    for feature, phrases in FEATURE_SYNONYMS.items():

        for phrase in phrases:

            if phrase in query:

                detected.append(feature)
                break

    return list(dict.fromkeys(detected))


# ============================================================
# BUDGET EXTRACTION
# ============================================================

def extract_budget(query):

    query = query.lower()

    # Examples:
    # under 3000
    # below ₹3000
    # less than 50000
    # within 60000
    # budget 50000
    # around 30000

    patterns = [

        r"(?:under|below|less\s+than|within)"
        r"\s*(?:₹|rs\.?|inr)?"
        r"\s*([\d,]+(?:\.\d+)?)",

        r"(?:budget|price)"
        r"\s*(?:of|is|around|near)?"
        r"\s*(?:₹|rs\.?|inr)?"
        r"\s*([\d,]+(?:\.\d+)?)",

        r"(?:₹|rs\.?|inr)"
        r"\s*([\d,]+(?:\.\d+)?)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            query
        )

        if match:

            value = match.group(1)

            try:

                return float(
                    value.replace(",", "")
                )

            except ValueError:

                pass

    return None


# ============================================================
# PRICE PREFERENCE
# ============================================================

def extract_price_preference(query):

    query = query.lower()

    if any(
        phrase in query
        for phrase in [
            "cheapest",
            "lowest price",
            "budget option",
            "affordable",
            "cheap"
        ]
    ):

        return "cheapest"

    if any(
        phrase in query
        for phrase in [
            "best",
            "premium",
            "top",
            "highest quality",
            "flagship"
        ]
    ):

        return "best"

    return "balanced"


# ============================================================
# KEYWORD EXTRACTION
# ============================================================

STOP_WORDS = {

    "i",
    "am",
    "im",
    "i'm",
    "looking",
    "look",
    "for",
    "something",
    "that",
    "is",
    "a",
    "an",
    "the",
    "with",
    "under",
    "below",
    "less",
    "than",
    "within",
    "please",
    "need",
    "want",
    "prefer",
    "preferably",
    "can",
    "you",
    "find",
    "me",
    "show",
    "my",
    "to",
    "use",
    "using",
    "buy",
    "get",
    "give",
    "recommend",
    "recommendation",
    "suggest",
    "suggestion",
    "something",
    "good",
    "best",
    "for",
    "price",
    "budget",
    "around",
    "near",
    "under"
}


def extract_keywords(query):

    words = re.findall(
        r"[a-zA-Z0-9]+",
        query.lower()
    )

    keywords = []

    for word in words:

        if word in STOP_WORDS:
            continue

        if word.isdigit():
            continue

        if len(word) <= 2:
            continue

        keywords.append(word)

    return list(
        dict.fromkeys(keywords)
    )


# ============================================================
# COMPLETE INTENT EXTRACTION
# ============================================================

def extract_intent(query):

    query = str(query).strip()

    budget = extract_budget(query)

    categories = detect_category(query)

    use_cases = detect_use_case(query)

    features = detect_features(query)

    keywords = extract_keywords(query)

    price_preference = extract_price_preference(query)

    return {

        "query": query,

        "budget": budget,

        "categories": categories,

        "use_cases": use_cases,

        "features": features,

        "keywords": keywords,

        "price_preference": price_preference
    }


# ============================================================
# PRODUCT CATEGORY MATCH
# ============================================================

def category_matches(product, categories):

    if not categories:
        return False

    text = product_text(product)

    category = (
        product.get(
            "category",
            ""
        )
        .lower()
    )

    for wanted in categories:

        if wanted in category:
            return True

        if wanted in text:
            return True

    return False


# ============================================================
# FEATURE MATCHING
# ============================================================

def feature_matches(
    product,
    feature
):

    text = product_text(product)

    phrases = FEATURE_SYNONYMS.get(
        feature,
        [feature]
    )

    return any(
        phrase in text
        for phrase in phrases
    )


# ============================================================
# PRODUCT SCORING
# ============================================================

def calculate_product_score(
    product,
    intent
):

    name = (
        product.get(
            "name",
            ""
        )
        .lower()
    )

    category = (
        product.get(
            "category",
            ""
        )
        .lower()
    )

    description = (
        product.get(
            "description",
            ""
        )
        .lower()
    )

    searchable_text = product_text(
        product
    )

    score = 0

    matched_keywords = []

    matched_features = []

    # --------------------------------------------------------
    # 1. CATEGORY MATCH
    # --------------------------------------------------------

    categories = intent.get(
        "categories",
        []
    )

    if categories:

        if category_matches(
            product,
            categories
        ):

            score += 60

        else:

            score -= 20

    # --------------------------------------------------------
    # 2. KEYWORD MATCH
    # --------------------------------------------------------

    for keyword in intent.get(
        "keywords",
        []
    ):

        if keyword in name:

            score += 30

            matched_keywords.append(
                keyword
            )

        elif keyword in category:

            score += 20

            matched_keywords.append(
                keyword
            )

        elif keyword in description:

            score += 10

            matched_keywords.append(
                keyword
            )

        elif keyword in searchable_text:

            score += 5

            matched_keywords.append(
                keyword
            )

    # --------------------------------------------------------
    # 3. USE CASE
    # --------------------------------------------------------

    use_cases = intent.get(
        "use_cases",
        []
    )

    for use_case in use_cases:

        relevant_products = (
            USE_CASE_PRODUCTS.get(
                use_case,
                []
            )
        )

        matched_use_case = False

        for product_type in relevant_products:

            if product_type in searchable_text:

                score += 20
                matched_use_case = True
                break

        if matched_use_case:

            score += 10

    # --------------------------------------------------------
    # 4. FEATURE MATCH
    # --------------------------------------------------------

    for feature in intent.get(
        "features",
        []
    ):

        if feature_matches(
            product,
            feature
        ):

            score += 25

            matched_features.append(
                feature
            )

        else:

            # Requirement explicitly requested
            # but product doesn't mention it.
            score -= 8

    # --------------------------------------------------------
    # 5. BUDGET
    # --------------------------------------------------------

    price = safe_float(
        product.get(
            "price",
            0
        )
    )

    budget = intent.get(
        "budget"
    )

    if budget is not None:

        if price <= budget:

            score += 30

            if budget > 0:

                usage = (
                    price / budget
                )

                if usage >= 0.85:

                    score += 12

                elif usage >= 0.70:

                    score += 8

                elif usage >= 0.50:

                    score += 4

        else:

            score -= 80

    # --------------------------------------------------------
    # 6. PRICE PREFERENCE
    # --------------------------------------------------------

    price_preference = intent.get(
        "price_preference"
    )

    if price_preference == "cheapest":

        if budget:

            ratio = price / budget

            if ratio <= 0.50:
                score += 20

            elif ratio <= 0.75:
                score += 10

    # --------------------------------------------------------
    # 7. STOCK
    # --------------------------------------------------------

    stock = safe_int(
        product.get(
            "stock",
            0
        )
    )

    if stock > 0:

        score += 15

    else:

        score -= 100

    # --------------------------------------------------------
    # 8. SPECIAL FEATURES
    # --------------------------------------------------------

    if (
        "wireless"
        in intent.get(
            "features",
            []
        )
    ):

        if "wireless" in searchable_text:

            score += 20

    if (
        "bluetooth"
        in intent.get(
            "features",
            []
        )
    ):

        if "bluetooth" in searchable_text:

            score += 20

    if (
        "noise cancellation"
        in intent.get(
            "features",
            []
        )
    ):

        if (
            "noise cancellation"
            in searchable_text
            or "anc" in searchable_text
        ):

            score += 20

    # --------------------------------------------------------
    # STORE MATCHING INFORMATION
    # --------------------------------------------------------

    product["_matched_keywords"] = list(
        dict.fromkeys(
            matched_keywords
        )
    )

    product["_matched_features"] = list(
        dict.fromkeys(
            matched_features
        )
    )

    return round(
        score,
        2
    )


# ============================================================
# RECOMMENDATION EXPLANATION
# ============================================================

def generate_reason(
    product,
    intent,
    score
):

    name = product.get(
        "name",
        "This product"
    )

    price = safe_float(
        product.get(
            "price",
            0
        )
    )

    reasons = []

    budget = intent.get(
        "budget"
    )

    # --------------------------------------------------------
    # Budget explanation
    # --------------------------------------------------------

    if budget is not None:

        if price <= budget:

            remaining = (
                budget - price
            )

            reasons.append(
                f"within your ₹{budget:.0f} budget"
            )

            if remaining > 0:

                reasons.append(
                    f"₹{remaining:.0f} under your limit"
                )

    # --------------------------------------------------------
    # Category
    # --------------------------------------------------------

    categories = intent.get(
        "categories",
        []
    )

    if categories:

        if category_matches(
            product,
            categories
        ):

            reasons.append(
                "matches your requested product type"
            )

    # --------------------------------------------------------
    # Use case
    # --------------------------------------------------------

    use_cases = intent.get(
        "use_cases",
        []
    )

    for use_case in use_cases:

        relevant_products = (
            USE_CASE_PRODUCTS.get(
                use_case,
                []
            )
        )

        if any(
            product_type
            in product_text(product)
            for product_type
            in relevant_products
        ):

            reasons.append(
                f"suitable for {use_case}"
            )

    # --------------------------------------------------------
    # Matched features
    # --------------------------------------------------------

    matched_features = product.get(
        "_matched_features",
        []
    )

    if matched_features:

        readable = ", ".join(
            matched_features[:3]
        )

        reasons.append(
            f"matches requested features: {readable}"
        )

    # --------------------------------------------------------
    # Matched keywords
    # --------------------------------------------------------

    matched_keywords = product.get(
        "_matched_keywords",
        []
    )

    if matched_keywords:

        readable = ", ".join(
            matched_keywords[:3]
        )

        reasons.append(
            f"matches keywords such as {readable}"
        )

    # --------------------------------------------------------
    # Stock
    # --------------------------------------------------------

    stock = safe_int(
        product.get(
            "stock",
            0
        )
    )

    if stock > 0:

        reasons.append(
            "currently in stock"
        )

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    if not reasons:

        return (
            f"{name} matches your search."
        )

    return (
        f"{name} is recommended because it "
        + ", ".join(reasons)
        + "."
    )


# ============================================================
# CONFIDENCE SCORE
# ============================================================

def calculate_confidence(
    intent,
    results
):

    confidence = 0

    if intent.get(
        "categories"
    ):

        confidence += 30

    if intent.get(
        "budget"
    ) is not None:

        confidence += 20

    if intent.get(
        "use_cases"
    ):

        confidence += 15

    if intent.get(
        "features"
    ):

        confidence += 15

    if intent.get(
        "keywords"
    ):

        confidence += 10

    if results:

        confidence += 10

    return min(
        confidence,
        100
    )


# ============================================================
# CLEAN PRODUCT FOR API
# ============================================================

def clean_product(product):

    cleaned = {}

    for key, value in product.items():

        if key.startswith("_"):

            continue

        cleaned[key] = value

    return cleaned


def recommendation_metadata(product, intent):

    price = safe_float(product.get("price", 0))
    budget = intent.get("budget")
    category_fit = 100 if category_matches(product, intent.get("categories", [])) else 55
    budget_fit = 100 if budget is None else max(0, min(100, round((budget - max(0, price - budget)) / budget * 100))) if budget else 0
    feature_count = len(intent.get("features", []))
    matched_feature_count = len(product.get("_matched_features", []))
    feature_fit = 100 if not feature_count else round(matched_feature_count / feature_count * 100)
    rating = max(0, min(100, round(safe_float(product.get("rating", 4)) / 5 * 100)))
    match_score = max(0, min(99, round((category_fit * 0.35) + (budget_fit * 0.3) + (feature_fit * 0.2) + (rating * 0.15))))

    product["match_percent"] = match_score
    product["score_breakdown"] = {
        "Category fit": category_fit,
        "Budget fit": budget_fit,
        "Requested features": feature_fit,
        "Customer rating": rating,
    }


# ============================================================
# SMART SHOPPING AGENT
# ============================================================

def shopping_agent(
    user_query: str
):

    # --------------------------------------------------------
    # Validate query
    # --------------------------------------------------------

    if not user_query or not str(
        user_query
    ).strip():

        return {

            "success": False,

            "message":
                "Please tell me what product you are looking for.",

            "intent": {},

            "results": []
        }

    # --------------------------------------------------------
    # Load products
    # --------------------------------------------------------

    try:

        products = load_products()

    except Exception as error:

        return {

            "success": False,

            "message":
                f"Unable to load product dataset: {error}",

            "intent": {},

            "results": []
        }

    # --------------------------------------------------------
    # Understand query
    # --------------------------------------------------------

    intent = extract_intent(
        user_query
    )

    # --------------------------------------------------------
    # Score products
    # --------------------------------------------------------

    scored_products = []

    for original_product in products:

        product = original_product.copy()

        score = calculate_product_score(
            product,
            intent
        )

        product["ranking_score"] = score

        scored_products.append(
            product
        )

    # --------------------------------------------------------
    # STRICT BUDGET FILTER
    # --------------------------------------------------------

    budget = intent.get(
        "budget"
    )

    if budget is not None:

        scored_products = [

            product

            for product
            in scored_products

            if safe_float(
                product.get(
                    "price",
                    0
                )
            ) <= budget

        ]

    # --------------------------------------------------------
    # REMOVE OUT-OF-STOCK
    # --------------------------------------------------------

    scored_products = [

        product

        for product
        in scored_products

        if safe_int(
            product.get(
                "stock",
                0
            )
        ) > 0

    ]

    # --------------------------------------------------------
    # REMOVE ZERO-RELEVANCE RESULTS
    # --------------------------------------------------------

    relevant_products = [

        product

        for product
        in scored_products

        if product.get(
            "ranking_score",
            0
        ) > 0

    ]

    # --------------------------------------------------------
    # If strict matching gives nothing,
    # use broader matching.
    # --------------------------------------------------------

    if not relevant_products:

        broader_products = [

            product

            for product
            in scored_products

            if product.get(
                "ranking_score",
                0
            ) >= 0

        ]

        relevant_products = (
            broader_products
        )

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    relevant_products.sort(

        key=lambda product:
            product.get(
                "ranking_score",
                0
            ),

        reverse=True
    )

    # --------------------------------------------------------
    # TOP RESULTS
    # --------------------------------------------------------

    top_results = (
        relevant_products[:10]
    )

    # --------------------------------------------------------
    # Add recommendation explanations
    # --------------------------------------------------------

    for product in top_results:

        product["recommendation"] = (
            generate_reason(
                product,
                intent,
                product.get(
                    "ranking_score",
                    0
                )
            )
        )

        product["price_value"] = safe_float(
            product.get(
                "price",
                0
            )
        )

        product["stock_available"] = safe_int(
            product.get(
                "stock",
                0
            )
        )
        recommendation_metadata(product, intent)

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    confidence = calculate_confidence(
        intent,
        top_results
    )

    # --------------------------------------------------------
    # No result
    # --------------------------------------------------------

    if not top_results:

        message = (
            "I couldn't find a suitable product "
            "matching all your requirements."
        )

        if budget is not None:

            message += (
                f" Try increasing your ₹{budget:.0f} budget "
                "or removing one requirement."
            )

        return {

            "success": False,

            "message": message,

            "intent": intent,

            "confidence": confidence,

            "results": []
        }

    # --------------------------------------------------------
    # Best product
    # --------------------------------------------------------

    best_product = top_results[0]

    best_product_name = best_product.get(
        "name",
        "the top result"
    )

    # --------------------------------------------------------
    # User-friendly message
    # --------------------------------------------------------

    if len(top_results) == 1:

        message = (
            f"I found 1 suitable product: "
            f"{best_product_name}."
        )

    else:

        message = (
            f"I found {len(top_results)} suitable "
            f"products. {best_product_name} is "
            "my top recommendation based on your requirements."
        )

    # --------------------------------------------------------
    # Clean API response
    # --------------------------------------------------------

    cleaned_results = [

        clean_product(product)

        for product in top_results

    ]

    # --------------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------------

    return {

        "success": True,

        "message": message,

        "confidence": confidence,

        "intent": {

            "query":
                intent["query"],

            "budget":
                intent["budget"],

            "categories":
                intent["categories"],

            "use_cases":
                intent["use_cases"],

            "features":
                intent["features"],

            "keywords":
                intent["keywords"],

            "price_preference":
                intent["price_preference"]
        },

        "top_recommendation":
            clean_product(
                best_product
            ),

        "results":
            cleaned_results
    }


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("PAYPILOT AI - SMART SHOPPING ENGINE")
    print("=" * 60)

    test_queries = [

        "wireless headphones under 3000 for gaming",

        "laptop under 60000 for coding",

        "best headphones under 5000 with good battery",

        "keyboard for gaming under 3000",

        "laptop for college student under 50000"
    ]

    for query in test_queries:

        print()
        print("-" * 60)
        print("QUERY:")
        print(query)

        result = shopping_agent(
            query
        )

        print()
        print("SUCCESS:")
        print(result["success"])

        print()
        print("INTENT:")
        print(result.get("intent"))

        print()
        print("MESSAGE:")
        print(result["message"])

        if result.get(
            "results"
        ):

            print()
            print("TOP RESULTS:")

            for index, product in enumerate(
                result["results"][:3],
                start=1
            ):

                print(
                    f"{index}. "
                    f"{product.get('name')} "
                    f"- ₹{product.get('price')} "
                    f"- Score: "
                    f"{product.get('ranking_score')}"
                )

                print(
                    f"   {product.get('recommendation')}"
                )

    print()
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)