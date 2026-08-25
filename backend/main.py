import json
import uuid
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.agent import shopping_agent, load_products
from backend.product_engine import get_product_by_id
from backend.payment import create_payment

from database.db import (
    init_db,
    save_order,
    get_all_orders,
    get_order,
    update_order_status,
)


# ============================================================
# INITIALIZE DATABASE
# ============================================================

init_db()


# ============================================================
# CREATE APP
# ============================================================

app = FastAPI(
    title="PayPilot AI",
    description="AI-powered agentic commerce assistant",
    version="3.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# IN-MEMORY CART
# ============================================================

cart = []
sessions = {}


# ============================================================
# REQUEST MODELS
# ============================================================

class SearchRequest(BaseModel):
    query: str


class CartItemRequest(BaseModel):
    product_name: str
    quantity: int = 1


class CheckoutRequest(BaseModel):
    customer_name: str
    phone: str
    address: str
    payment_method: str = "Cash on Delivery"


class StatusRequest(BaseModel):
    status: str


class CompareRequest(BaseModel):
    product_ids: list[int]


class SessionSearchRequest(SearchRequest):
    conversation_id: str = "default"


class PaymentRequest(BaseModel):
    amount: float
    payment_method: str = "Razorpay Test Mode"


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "Welcome to PayPilot AI",
        "status": "running",
        "version": "3.0.0",
        "features": [
            "AI Product Search",
            "Smart Product Ranking",
            "AI Recommendation Reasons",
            "Shopping Cart",
            "Checkout",
            "Order Placement",
            "Order History",
            "Order Tracking",
            "SQLite Database"
        ]
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "database": "connected"
    }


@app.get("/api/products")
def products():
    return {"success": True, "products": load_products()}


@app.get("/api/products/{product_id}")
def product_detail(product_id: int):
    product = get_product_by_id(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"success": True, "product": product}


@app.post("/api/products/compare")
def compare_products(request: CompareRequest):
    if len(request.product_ids) < 2 or len(request.product_ids) > 4:
        raise HTTPException(status_code=400, detail="Compare between 2 and 4 products")
    selected = [get_product_by_id(product_id) for product_id in request.product_ids]
    if any(product is None for product in selected):
        raise HTTPException(status_code=404, detail="One or more products not found")
    pick = max(selected, key=lambda product: float(product.get("rating", 0)))
    return {
        "success": True,
        "products": selected,
        "paypilot_pick": pick,
        "reason": f"{pick['name']} has the strongest customer rating among these options."
    }


# ============================================================
# AI AGENT
# ============================================================

@app.post("/agent")
def agent(request: SearchRequest):

    try:

        result = shopping_agent(request.query)

        return result

    except Exception as e:

        return {
            "success": False,
            "message": f"Agent error: {str(e)}",
            "intent": {},
            "results": []
        }


@app.post("/api/agent")
def session_agent(request: SessionSearchRequest):
    history = sessions.setdefault(request.conversation_id, [])
    history.append(request.query)
    result = shopping_agent(" ".join(history[-3:]))
    result["conversation_id"] = request.conversation_id
    result["history_length"] = len(history)
    return result


@app.post("/api/payment/create-order")
def create_test_payment(request: PaymentRequest):
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Payment amount must be greater than zero")
    return {"success": True, "mode": "test", "order": create_payment(request.amount, request.payment_method)}


@app.post("/api/payment/verify")
def verify_test_payment(request: PaymentRequest):
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Payment amount must be greater than zero")
    return {"success": True, "mode": "test", "status": "verified", "amount": request.amount}


# ============================================================
# SEARCH
# ============================================================

@app.post("/search")
def search(request: SearchRequest):

    try:

        result = shopping_agent(request.query)

        return result

    except Exception as e:

        return {
            "success": False,
            "message": f"Search error: {str(e)}",
            "intent": {},
            "results": []
        }


# ============================================================
# GET CART
# ============================================================

@app.get("/cart")
def get_cart():

    subtotal = 0

    for item in cart:

        subtotal += (
            item["price"] *
            item["quantity"]
        )

    return {
        "success": True,
        "items": cart,
        "subtotal": round(subtotal, 2),
        "total": round(subtotal, 2),
        "item_count": sum(
            item["quantity"]
            for item in cart
        )
    }


# ============================================================
# ADD TO CART
# ============================================================

@app.post("/cart/add")
def add_to_cart(request: CartItemRequest):

    if request.quantity < 1:

        raise HTTPException(
            status_code=400,
            detail="Quantity must be at least 1"
        )

    products = load_products()

    selected_product = None

    for product in products:

        if (
            product.get("name", "").lower()
            ==
            request.product_name.lower()
        ):

            selected_product = product
            break

    if selected_product is None:

        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    try:

        stock = int(
            selected_product.get(
                "stock",
                0
            )
        )

    except (ValueError, TypeError):

        stock = 0

    if stock <= 0:

        raise HTTPException(
            status_code=400,
            detail="Product is out of stock"
        )

    for item in cart:

        if (
            item["name"].lower()
            ==
            request.product_name.lower()
        ):

            new_quantity = (
                item["quantity"]
                +
                request.quantity
            )

            if new_quantity > stock:

                raise HTTPException(
                    status_code=400,
                    detail=f"Only {stock} item(s) available"
                )

            item["quantity"] = new_quantity

            return {
                "success": True,
                "message": "Product quantity updated",
                "cart": cart
            }

    try:

        price = float(
            selected_product.get(
                "price",
                0
            )
        )

    except (ValueError, TypeError):

        price = 0

    new_item = {

        "name": selected_product.get(
            "name",
            ""
        ),

        "category": selected_product.get(
            "category",
            ""
        ),

        "price": price,

        "description": selected_product.get(
            "description",
            ""
        ),

        "quantity": request.quantity
    }

    cart.append(new_item)

    return {
        "success": True,
        "message": "Product added to cart",
        "cart": cart
    }


# ============================================================
# REMOVE FROM CART
# ============================================================

@app.delete("/cart/remove/{product_name}")
def remove_from_cart(product_name: str):

    for index, item in enumerate(cart):

        if (
            item["name"].lower()
            ==
            product_name.lower()
        ):

            removed_item = cart.pop(index)

            return {
                "success": True,
                "message": (
                    f"{removed_item['name']} "
                    "removed from cart"
                ),
                "cart": cart
            }

    raise HTTPException(
        status_code=404,
        detail="Product not found in cart"
    )


# ============================================================
# UPDATE CART
# ============================================================

@app.put("/cart/update")
def update_cart(request: CartItemRequest):

    if request.quantity < 1:

        raise HTTPException(
            status_code=400,
            detail="Quantity must be at least 1"
        )

    products = load_products()

    stock = 0
    product_found = False

    for product in products:

        if (
            product.get("name", "").lower()
            ==
            request.product_name.lower()
        ):

            product_found = True

            try:

                stock = int(
                    product.get(
                        "stock",
                        0
                    )
                )

            except (ValueError, TypeError):

                stock = 0

            break

    if not product_found:

        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if request.quantity > stock:

        raise HTTPException(
            status_code=400,
            detail=f"Only {stock} item(s) available"
        )

    for item in cart:

        if (
            item["name"].lower()
            ==
            request.product_name.lower()
        ):

            item["quantity"] = request.quantity

            return {
                "success": True,
                "message": "Cart updated",
                "cart": cart
            }

    raise HTTPException(
        status_code=404,
        detail="Product not found in cart"
    )


# ============================================================
# CLEAR CART
# ============================================================

@app.delete("/cart/clear")
def clear_cart():

    cart.clear()

    return {
        "success": True,
        "message": "Cart cleared",
        "cart": []
    }


# ============================================================
# CHECKOUT PREVIEW
# ============================================================

@app.get("/checkout")
def checkout():

    if len(cart) == 0:

        return {
            "success": False,
            "message": "Your cart is empty.",
            "items": [],
            "subtotal": 0,
            "delivery_fee": 0,
            "total": 0
        }

    subtotal = 0

    for item in cart:

        subtotal += (
            item["price"] *
            item["quantity"]
        )

    if subtotal >= 1000:

        delivery_fee = 0

    else:

        delivery_fee = 50

    total = subtotal + delivery_fee

    return {
        "success": True,
        "message": "Checkout ready",
        "items": cart,
        "subtotal": round(subtotal, 2),
        "delivery_fee": delivery_fee,
        "total": round(total, 2)
    }


# ============================================================
# PLACE ORDER
# ============================================================

@app.post("/checkout")
def place_order(request: CheckoutRequest):

    if not request.customer_name.strip():

        raise HTTPException(
            status_code=400,
            detail="Customer name is required"
        )

    if not request.phone.strip():

        raise HTTPException(
            status_code=400,
            detail="Phone number is required"
        )

    if not request.address.strip():

        raise HTTPException(
            status_code=400,
            detail="Delivery address is required"
        )

    if len(cart) == 0:

        raise HTTPException(
            status_code=400,
            detail="Your cart is empty"
        )

    subtotal = 0

    for item in cart:

        subtotal += (
            item["price"] *
            item["quantity"]
        )

    if subtotal >= 1000:

        delivery_fee = 0

    else:

        delivery_fee = 50

    total = subtotal + delivery_fee

    order_id = (
        "PP-"
        +
        datetime.now().strftime("%Y%m%d")
        +
        "-"
        +
        uuid.uuid4().hex[:6].upper()
    )

    new_order = {

        "order_id": order_id,

        "customer_name":
            request.customer_name.strip(),

        "phone":
            request.phone.strip(),

        "address":
            request.address.strip(),

        "payment_method":
            request.payment_method,

        "items":
            json.dumps(
                cart,
                ensure_ascii=False
            ),

        "subtotal":
            round(subtotal, 2),

        "delivery_fee":
            delivery_fee,

        "total":
            round(total, 2),

        "status":
            "Order Placed",

        "created_at":
            datetime.now().isoformat()
    }

    try:

        save_order(new_order)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Could not save order: {str(e)}"
        )

    saved_order = new_order.copy()

    saved_order["items"] = cart.copy()

    cart.clear()

    return {

        "success": True,

        "message":
            "🎉 Order placed successfully!",

        "order_id":
            order_id,

        "order":
            saved_order
    }


# ============================================================
# ORDER HISTORY
# ============================================================

@app.get("/orders")
def get_orders():

    try:

        database_orders = get_all_orders()

        for order in database_orders:

            try:

                order["items"] = json.loads(
                    order["items"]
                )

            except Exception:

                order["items"] = []

        return {

            "success": True,

            "orders":
                database_orders,

            "order_count":
                len(database_orders)
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Could not load orders: {str(e)}"
        )


# ============================================================
# ORDER TRACKING
# ============================================================

@app.get("/orders/{order_id}")
def get_single_order(order_id: str):

    order = get_order(order_id)

    if order is None:

        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    try:

        order["items"] = json.loads(
            order["items"]
        )

    except Exception:

        order["items"] = []

    return {

        "success": True,

        "order": order
    }


# ============================================================
# UPDATE ORDER STATUS
# ============================================================

@app.put("/orders/{order_id}/status")
def change_order_status(
    order_id: str,
    request: StatusRequest
):

    allowed_statuses = [

        "Order Placed",

        "Processing",

        "Packed",

        "Shipped",

        "Out for Delivery",

        "Delivered",

        "Cancelled"
    ]

    if request.status not in allowed_statuses:

        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid order status",
                "allowed_statuses":
                    allowed_statuses
            }
        )

    order = get_order(order_id)

    if order is None:

        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    updated = update_order_status(
        order_id,
        request.status
    )

    if not updated:

        raise HTTPException(
            status_code=500,
            detail="Could not update order status"
        )

    updated_order = get_order(order_id)

    try:

        updated_order["items"] = json.loads(
            updated_order["items"]
        )

    except Exception:

        updated_order["items"] = []

    return {

        "success": True,

        "message":
            "Order status updated",

        "order":
            updated_order
    }


# ============================================================
# STARTUP MESSAGE
# ============================================================

@app.on_event("startup")
def startup_event():

    print("")
    print("==========================================")
    print("        PAYPILOT AI BACKEND")
    print("==========================================")
    print("Database: SQLite")
    print("Orders: Persistent")
    print("Order Tracking: Enabled")
    print("Order History: Enabled")
    print("==========================================")
    print("")