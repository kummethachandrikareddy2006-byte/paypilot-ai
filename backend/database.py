import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "paypilot.db"


def get_connection():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def init_db():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            order_id TEXT UNIQUE NOT NULL,

            customer_name TEXT NOT NULL,

            phone TEXT NOT NULL,

            address TEXT NOT NULL,

            payment_method TEXT NOT NULL,

            items TEXT NOT NULL,

            subtotal REAL NOT NULL,

            delivery_fee REAL NOT NULL,

            total REAL NOT NULL,

            status TEXT NOT NULL,

            created_at TEXT NOT NULL

        )
    """)

    connection.commit()

    connection.close()

    print("DATABASE OK")


def save_order(order):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO orders (

            order_id,
            customer_name,
            phone,
            address,
            payment_method,
            items,
            subtotal,
            delivery_fee,
            total,
            status,
            created_at

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        order["order_id"],
        order["customer_name"],
        order["phone"],
        order["address"],
        order["payment_method"],
        order["items"],
        order["subtotal"],
        order["delivery_fee"],
        order["total"],
        order["status"],
        order["created_at"]

    ))

    connection.commit()

    connection.close()


def get_all_orders():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *

        FROM orders

        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


def get_order(order_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *

        FROM orders

        WHERE order_id = ?
    """, (
        order_id,
    ))

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return dict(row)


def update_order_status(order_id, status):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE orders

        SET status = ?

        WHERE order_id = ?
    """, (
        status,
        order_id
    ))

    connection.commit()

    updated = cursor.rowcount > 0

    connection.close()

    return updated