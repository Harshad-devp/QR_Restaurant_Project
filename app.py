from flask import Flask, render_template, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "supersecretkey"

# -------------------------------
# Temporary Menu Database
# -------------------------------
menu_items = [
    {"id": 1, "name": "Margherita Pizza", "price": 199},
    {"id": 2, "name": "Veg Burger", "price": 99},
    {"id": 3, "name": "Pasta", "price": 149},
    {"id": 4, "name": "Cold Coffee", "price": 79}
]

# -------------------------------
# Home Page – Table Selection
# -------------------------------
@app.route("/")
def home():
    return render_template("index.html")

# -------------------------------
# Menu Page (Table-wise)
# -------------------------------
@app.route("/menu/<int:table_id>")
def menu(table_id):
    session["table_id"] = table_id
    return render_template(
        "menu.html",
        menu=menu_items,
        table_id=table_id,
        tables=session.get("tables", {})
    )

# -------------------------------
# Add Item to Cart (Table-wise)
# -------------------------------
@app.route("/add/<int:item_id>")
def add_to_cart(item_id):

    if "tables" not in session:
        session["tables"] = {}

    table_id = str(session["table_id"])

    if table_id not in session["tables"]:
        session["tables"][table_id] = {}

    cart = session["tables"][table_id]

    # find item price
    price = 0
    for item in menu_items:
        if item["id"] == item_id:
            price = item["price"]
            break

    if str(item_id) in cart:
        cart[str(item_id)]["qty"] += 1
    else:
        cart[str(item_id)] = {
            "price": price,
            "qty": 1
        }

    session["tables"][table_id] = cart
    session.modified = True   # 🔥 VERY IMPORTANT

    return redirect(url_for("menu", table_id=session["table_id"]))

# -------------------------------
# Remove Item from Cart (Table-wise)
# -------------------------------
@app.route("/remove/<int:item_id>")
def remove_from_cart(item_id):

    table_id = str(session["table_id"])

    if "tables" in session and table_id in session["tables"]:
        cart = session["tables"][table_id]
        cart.pop(str(item_id), None)
        session["tables"][table_id] = cart
        session.modified = True   # 🔥 VERY IMPORTANT

    return redirect(url_for("menu", table_id=session["table_id"]))

# -------------------------------
# Cart Page (Table-wise)
# -------------------------------
@app.route("/cart")
def cart():

    cart_data = []
    grand_total = 0
    table_id = str(session.get("table_id"))

    if "tables" in session and table_id in session["tables"]:
        for item_id, data in session["tables"][table_id].items():
            for item in menu_items:
                if item["id"] == int(item_id):
                    item_total = data["price"] * data["qty"]
                    grand_total += item_total
                    cart_data.append({
                        "id": item["id"],
                        "name": item["name"],
                        "price": data["price"],
                        "qty": data["qty"],
                        "total": item_total
                    })

    return render_template(
        "cart.html",
        cart=cart_data,
        grand_total=grand_total,
        table_id=table_id
    )

# -------------------------------
# Run Server
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
