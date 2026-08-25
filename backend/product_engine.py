import csv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
PRODUCTS_FILE = BASE_DIR / "data" / "products.csv"


def get_all_products():
    products = []

    if not PRODUCTS_FILE.exists():
        raise FileNotFoundError(
            f"Products file not found: {PRODUCTS_FILE}"
        )

    with open(
        PRODUCTS_FILE,
        mode="r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            row["id"] = int(row["id"])
            row["price"] = float(row["price"])
            row["stock"] = int(row["stock"])

            products.append(row)

    return products


def search_products(query: str):
    query = query.lower().strip()

    if not query:
        return get_all_products()

    products = get_all_products()

    results = []

    for product in products:

        searchable_text = " ".join([
            product["name"],
            product["category"],
            product["description"]
        ]).lower()

        if query in searchable_text:
            results.append(product)

    return results


def get_product_by_id(product_id: int):

    products = get_all_products()

    for product in products:

        if product["id"] == product_id:
            return product

    return None


def get_products_by_category(category: str):

    category = category.lower().strip()

    products = get_all_products()

    return [
        product
        for product in products
        if category in product["category"].lower()
    ]