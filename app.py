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
    if "cart" not in session:
        session["cart"] = []

    session["cart"].append(item_id)
    return redirect(url_for("menu"))

@app.route("/cart")
def cart():
    cart_items = []
    cart_ids = session.get("cart", [])

    for id in cart_ids:
        for item in menu_items:
            if item["id"] == id:
                cart_items.append(item)

    return render_template("cart.html", cart=cart_items)



if __name__ == "__main__":
    app.run(debug=True)
