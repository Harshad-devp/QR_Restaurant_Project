from flask import Flask, render_template, session, redirect, url_for, request

from database import init_db, get_db_connection
from flask import request

app = Flask(__name__)
app.secret_key = "supersecretkey"

# =================================================
# Home Page – Table Selection
# =================================================
@app.route("/")
def home():
    return render_template("index.html")

# =================================================
# Menu Page (Table-wise) – DB BASED
# =================================================
@app.route("/menu/<int:table_id>")
def menu(table_id):
    session["table_id"] = table_id

    conn = get_db_connection()
    menu_items = conn.execute(
        "SELECT id, name, price FROM menu"
    ).fetchall()
    conn.close()

    return render_template(
        "menu.html",
        menu=menu_items,
        table_id=table_id,
        tables=session.get("tables", {})
    )

# =================================================
# Add Item to Cart (Table-wise)
# =================================================
@app.route("/add/<int:item_id>")
def add_to_cart(item_id):

    if "tables" not in session:
        session["tables"] = {}

    table_id = str(session["table_id"])

    if table_id not in session["tables"]:
        session["tables"][table_id] = {}

    cart = session["tables"][table_id]

    conn = get_db_connection()
    item = conn.execute(
        "SELECT price FROM menu WHERE id = ?",
        (item_id,)
    ).fetchone()
    conn.close()

    if not item:
        return redirect(url_for("menu", table_id=session["table_id"]))

    if str(item_id) in cart:
        cart[str(item_id)]["qty"] += 1
    else:
        cart[str(item_id)] = {
            "price": item["price"],
            "qty": 1
        }

    session["tables"][table_id] = cart
    session.modified = True

    return redirect(url_for("menu", table_id=session["table_id"]))

# =================================================
# Remove Item from Cart
# =================================================
@app.route("/remove/<int:item_id>")
def remove_from_cart(item_id):

    table_id = str(session["table_id"])

    if "tables" in session and table_id in session["tables"]:
        session["tables"][table_id].pop(str(item_id), None)
        session.modified = True

    return redirect(url_for("menu", table_id=session["table_id"]))

# =================================================
# Cart Page
# =================================================
@app.route("/cart")
def cart():

    cart_data = []
    grand_total = 0
    table_id = str(session.get("table_id"))

    if "tables" in session and table_id in session["tables"]:

        conn = get_db_connection()

        for item_id, data in session["tables"][table_id].items():
            item = conn.execute(
                "SELECT name FROM menu WHERE id = ?",
                (item_id,)
            ).fetchone()

            if item:
                total = data["price"] * data["qty"]
                grand_total += total
                cart_data.append({
                    "name": item["name"],
                    "qty": data["qty"],
                    "price": data["price"],
                    "total": total
                })

        conn.close()

    return render_template(
        "cart.html",
        cart=cart_data,
        grand_total=grand_total,
        table_id=table_id
    )

# =================================================
# Admin Dashboard – Live Orders
# =================================================
@app.route("/admin")
def admin_dashboard():

    tables = session.get("tables", {})
    admin_data = []

    conn = get_db_connection()

    for table_id, cart in tables.items():
        table_total = 0
        items = []

        for item_id, data in cart.items():
            item = conn.execute(
                "SELECT name FROM menu WHERE id = ?",
                (item_id,)
            ).fetchone()

            if item:
                total = data["price"] * data["qty"]
                table_total += total
                items.append({
                    "name": item["name"],
                    "qty": data["qty"],
                    "total": total
                })

        admin_data.append({
            "table_id": table_id,
            "items": items,
            "total": table_total
        })

    conn.close()

    return render_template("admin.html", tables=admin_data)

from flask import request

@app.route("/admin/add", methods=["POST"])
def admin_add_item():
    name = request.form["name"]
    price = request.form["price"]

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO menu (name, price) VALUES (?, ?)",
        (name, price)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("admin_dashboard"))


# =================================================
# Run Server
# =================================================
if __name__ == "__main__":
    init_db()        # ✅ ONLY ONCE
    app.run(debug=True)
