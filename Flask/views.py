from flask import render_template
from Flask import app


# Landing Page
@app.route("/", methods=["POST", "GET"])
def index():
    return render_template("index.html")

# May not be needed
# # Registration Page
# @app.route("/register", methods=["POST", "GET"])
# def register():
#     return render_template("register.html")


# Home Page
@app.route("/home", methods=["POST", "GET"])
def home():
    return render_template("home.html")


# Comparison Page
@app.route("/compare", methods=["POST", "GET"])
def compare():
    return render_template("compare.html")