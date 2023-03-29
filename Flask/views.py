from flask import render_template
# from flask_login import logout_user
from Flask import app
from Database.db import *


# Landing Page
@app.route("/", methods=["POST", "GET"])
def index():
    print(getUsers())
    return render_template("index.html")

# # Logout
# @app.route('/logout', methods=['POST'])
# def logout():
#     logout_user()
#     return redirect(url_for('index'))


# Home Page
@app.route("/home", methods=["POST", "GET"])
def home():
    # Testcase
    username = "John"
    friendFirst_1 = "Sophia"
    friendLast_1 = "Robertson"
    friendScore_1 = 98
    friendTrack_1 = "Flowers"
    friendFirst_2 = "Lucas"
    friendLast_2 = "Johnson"
    friendScore_2 = 85
    friendTrack_2 = "Kill Bill"
    friendFirst_3 = "Aria"
    friendLast_3 = "Patel"
    friendScore_3 = 80
    friendTrack_3 = "Boy's A Liar, Pt. 2"
    friendFirst_4 = "Ethan"
    friendLast_4 = "Baker"
    friendScore_4 = 70
    friendTrack_4 = "Creepin'"
    friendFirst_5 = "Ava"
    friendLast_5 = "Kim"
    friendScore_5 = 10
    friendTrack_5 = "Morgan Wallen"
    # Code
    return render_template(
        "home.html",
        username = username,
        friendFirst_1 = friendFirst_1,
        friendLast_1 = friendLast_1,
        friendScore_1 = friendScore_1,
        friendTrack_1 = friendTrack_1,
        friendFirst_2 = friendFirst_2,
        friendLast_2 = friendLast_2,
        friendScore_2 = friendScore_2,
        friendTrack_2 = friendTrack_2,
        friendFirst_3 = friendFirst_3,
        friendLast_3 = friendLast_3,
        friendScore_3 = friendScore_3,
        friendTrack_3 = friendTrack_3,
        friendFirst_4 = friendFirst_4,
        friendLast_4 = friendLast_4,
        friendScore_4 = friendScore_4,
        friendTrack_4 = friendTrack_4,
        friendFirst_5 = friendFirst_5,
        friendLast_5 = friendLast_5,
        friendScore_5 = friendScore_5,
        friendTrack_5 = friendTrack_5,
        )


# Comparison Page
@app.route("/compare", methods=["POST", "GET"])
def compare():
    return render_template("compare.html")