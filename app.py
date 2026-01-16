from flask import Flask, render_template

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)
