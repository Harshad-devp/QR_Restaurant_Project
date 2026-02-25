import sqlite3


def get_db_connection():
    conn = sqlite3.connect("restaurant.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    # =============================
    # MENU TABLE (WITH IMAGE)
    # =============================
    conn.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            image TEXT NOT NULL
        )
    """)

    # =============================
    # ORDERS TABLE (UPDATED WITH NOTE)
    # =============================
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_id INTEGER NOT NULL,
            total REAL NOT NULL,
            note TEXT
        )
    """)

    # =============================
    # ORDER ITEMS TABLE
    # =============================
    conn.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            item_name TEXT,
            qty INTEGER,
            price REAL
        )
    """)

    conn.commit()
    conn.close()