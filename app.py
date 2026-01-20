from flask import Flask, render_template, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Temprory database 
menu_items = [
    {"id": 1, "name": "Margherita Pizza", "price": 199},
    {"id": 2, "name": "Veg Burger", "price": 99},
    {"id": 3, "name": "Pasta", "price": 149},
    {"id": 4, "name": "Cold Coffee", "price": 79}
]
# page rendring route or HOME route
@app.route("/")
def home():
    return render_template("index.html")

# Route for menu html
@app.route("/menu")
def menu():
    return render_template("menu.html", menu=menu_items)

@app.route("/add/<int:item_id>")
def add_to_cart(item_id):

    # FORCE reset if cart is list (Day 5 leftover)
    if "cart" not in session or isinstance(session["cart"], list):
        session["cart"] = {}

    cart = session["cart"]

    # Get correct price from menu_items
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


if __name__ == "__main__":
    app.run(debug=True)
