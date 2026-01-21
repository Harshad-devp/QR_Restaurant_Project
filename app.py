from flask import Flask, render_template, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Temporary database
menu_items = [
    {"id": 1, "name": "Margherita Pizza", "price": 199},
    {"id": 2, "name": "Veg Burger", "price": 99},
    {"id": 3, "name": "Pasta", "price": 149},
    {"id": 4, "name": "Cold Coffee", "price": 79}
]

# Home route
@app.route("/")
def home():
    return render_template("index.html")

# Menu route
@app.route("/menu")
def menu():
    return render_template("menu.html", menu=menu_items)

# Add to cart
@app.route("/add/<int:item_id>")
def add_to_cart(item_id):

    if "cart" not in session or isinstance(session["cart"], list):
        session["cart"] = {}

    cart = session["cart"]

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

    session["cart"] = cart
    return redirect(url_for("menu"))

# Remove from cart
@app.route("/remove/<int:item_id>")
def remove_from_cart(item_id):

    if "cart" in session:
        cart = session["cart"]
        cart.pop(str(item_id), None)
        session["cart"] = cart

    return redirect(url_for("menu"))

# Cart page
@app.route("/cart")
def cart():

    cart_data = []
    grand_total = 0

    if "cart" in session:
        for item_id, data in session["cart"].items():
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
        grand_total=grand_total
    )

if __name__ == "__main__":
    app.run(debug=True)
