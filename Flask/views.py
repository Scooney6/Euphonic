from flask import render_template
from Flask import app
from Database.db import *


# Landing Page
@app.route("/", methods=["POST", "GET"])
def index():
    print(getUsers())
    return render_template("index.html")


# Registration Page
@app.route("/register", methods=["POST", "GET"])
def register():
    return render_template("register.html")


# Home Page
@app.route("/home", methods=["POST", "GET"])
def home():
    return render_template("home.html")


# Comparison Page
@app.route("/compare", methods=["POST", "GET"])
def compare():
    return render_template("compare.html")


# Callback route
@app.route("/callback", methods=["POST", "GET"])
def callback():
    pass
