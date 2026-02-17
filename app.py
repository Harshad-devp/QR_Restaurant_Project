from flask import Flask, render_template, session, redirect, url_for, request
from database import init_db, get_db_connection

app = Flask(__name__)
app.secret_key = "supersecretkey"


# =================================================
# Home Page
# =================================================
@app.route("/")
def home():
    return render_template("index.html")


# =================================================
# Menu Page
# =================================================
@app.route("/menu/<int:table_id>")
def menu(table_id):

    session["table_id"] = table_id

    conn = get_db_connection()
    items = conn.execute("SELECT * FROM menu").fetchall()
    conn.close()

    return render_template(
        "menu.html",
        menu=items,
        table_id=table_id,
        tables=session.get("tables", {})
    )


# =================================================
# Add Item to Cart
# =================================================
@app.route("/add/<int:item_id>")
def add_to_cart(item_id):

    if "table_id" not in session:
        return redirect(url_for("home"))

    table_id = str(session["table_id"])

    if "tables" not in session:
        session["tables"] = {}

    if table_id not in session["tables"]:
        session["tables"][table_id] = {}

    cart = session["tables"][table_id]

    conn = get_db_connection()
    item = conn.execute(
        "SELECT name, price FROM menu WHERE id=?",
        (item_id,)
    ).fetchone()
    conn.close()

    if not item:
        return redirect(url_for("menu", table_id=table_id))

    if str(item_id) in cart:
        cart[str(item_id)]["qty"] += 1
    else:
        cart[str(item_id)] = {
            "name": item["name"],
            "price": item["price"],
            "qty": 1
        }

    session["tables"][table_id] = cart
    session.modified = True

    return redirect(url_for("menu", table_id=table_id))


# =================================================
# Increase Quantity
# =================================================
@app.route("/increase/<int:item_id>")
def increase_item(item_id):

    if "table_id" not in session:
        return redirect(url_for("home"))

    table_id = str(session["table_id"])

    if "tables" in session and table_id in session["tables"]:
        cart = session["tables"][table_id]

        if str(item_id) in cart:
            cart[str(item_id)]["qty"] += 1

        session["tables"][table_id] = cart
        session.modified = True

    return redirect(url_for("menu", table_id=table_id))


# =================================================
# Decrease Quantity
# =================================================
@app.route("/decrease/<int:item_id>")
def decrease_item(item_id):

    if "table_id" not in session:
        return redirect(url_for("home"))

    table_id = str(session["table_id"])

    if "tables" in session and table_id in session["tables"]:
        cart = session["tables"][table_id]

        if str(item_id) in cart:
            cart[str(item_id)]["qty"] -= 1

            if cart[str(item_id)]["qty"] <= 0:
                cart.pop(str(item_id))

        session["tables"][table_id] = cart
        session.modified = True

    return redirect(url_for("menu", table_id=table_id))


# =================================================
# Cart Page
# =================================================
@app.route("/cart")
def cart():

    if "table_id" not in session:
        return redirect(url_for("home"))

    table_id = str(session["table_id"])
    cart_data = []
    grand_total = 0

    if "tables" in session and table_id in session["tables"]:

        for item_id, data in session["tables"][table_id].items():
            total = data["price"] * data["qty"]
            grand_total += total

            cart_data.append({
                "id": item_id,
                "name": data["name"],
                "qty": data["qty"],
                "price": data["price"],
                "total": total
            })

    return render_template(
        "cart.html",
        cart=cart_data,
        grand_total=grand_total,
        table_id=table_id
    )


# =================================================
# Place Order
# =================================================
@app.route("/place_order", methods=["POST"])
def place_order():

    if "table_id" not in session:
        return redirect(url_for("home"))

    table_id = str(session["table_id"])

    if "tables" not in session or table_id not in session["tables"]:
        return redirect(url_for("menu", table_id=table_id))

    cart = session["tables"][table_id]

    if not cart:
        return redirect(url_for("menu", table_id=table_id))

    conn = get_db_connection()

    # Calculate total
    grand_total = sum(
        data["price"] * data["qty"] for data in cart.values()
    )

    # Insert order
    cursor = conn.execute(
        "INSERT INTO orders (table_id, total) VALUES (?, ?)",
        (table_id, grand_total)
    )
    order_id = cursor.lastrowid

    # Insert order items
    for data in cart.values():
        conn.execute(
            "INSERT INTO order_items (order_id, item_name, qty, price) VALUES (?, ?, ?, ?)",
            (order_id, data["name"], data["qty"], data["price"])
        )

    conn.commit()
    conn.close()

    # Clear cart
    session["tables"][table_id] = {}
    session.modified = True

    return redirect(url_for("menu", table_id=table_id))


# =================================================
# Admin Dashboard
# =================================================
@app.route("/admin")
def admin_dashboard():

    conn = get_db_connection()

    menu_items = conn.execute(
        "SELECT id, name, price, category FROM menu"
    ).fetchall()

    orders = conn.execute(
        "SELECT * FROM orders ORDER BY id DESC"
    ).fetchall()

    order_details = {}

    for order in orders:
        items = conn.execute(
            "SELECT item_name, qty, price FROM order_items WHERE order_id=?",
            (order["id"],)
        ).fetchall()

        order_details[order["id"]] = items

    conn.close()

    return render_template(
        "admin.html",
        menu=menu_items,
        orders=orders,
        order_details=order_details
    )


# =================================================
# Admin Add Item
# =================================================
@app.route("/admin/add", methods=["POST"])
def admin_add_item():

    name = request.form.get("name")
    price = request.form.get("price")
    category = request.form.get("category")

    if not name or not price or not category:
        return redirect(url_for("admin_dashboard"))

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO menu (name, price, category) VALUES (?, ?, ?)",
        (name, price, category)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("admin_dashboard"))


# =================================================
# Admin Delete Item
# =================================================
@app.route("/admin/delete/<int:item_id>")
def admin_delete_item(item_id):

    conn = get_db_connection()
    conn.execute("DELETE FROM menu WHERE id=?", (item_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("admin_dashboard"))


# =================================================
# Complete Order (Mark as Served)
# =================================================
@app.route("/admin/complete_order/<int:order_id>")
def complete_order(order_id):

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM order_items WHERE order_id=?",
        (order_id,)
    )

    conn.execute(
        "DELETE FROM orders WHERE id=?",
        (order_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin_dashboard"))


# =================================================
# Run Server
# =================================================
if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
