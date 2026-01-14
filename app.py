from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "QR Restaurant Ordering System - Day 1 Success 🚀"

if __name__ == '__main__':
    app.run(debug=True)
