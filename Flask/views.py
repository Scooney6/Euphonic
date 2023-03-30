from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, request, g
from flask_login import logout_user, login_required, current_user
from Flask import app
from Database.db import *


# Login Page
@app.route("/", methods=["POST", "GET"])
def login():
    services = ['Spotify', 'Apple Music', 'Tidal', 'Google Play Music', 'Amazon Music', 'More to come!']
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.get_user(username)
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
    return render_template('index.html', services = services)


# Logout
@app.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))


# Home Page
@app.route("/home", methods=["POST", "GET"])
@login_required
def home():
    # Testcase
    username = current_user.username
    friends = [
        {
            "first_name": "Sophia",
            "last_name": "Robertson",
            "score": 98,
            "track": "Flowers"
        },
        {
            "first_name": "Lucas",
            "last_name": "Johnson",
            "score": 85,
            "track": "Kill Bill"
        },
        {
            "first_name": "Aria",
            "last_name": "Patel",
            "score": 80,
            "track": "Boy's A Liar, Pt. 2"
        },
        {
            "first_name": "Ethan",
            "last_name": "Baker",
            "score": 70,
            "track": "Creepin'"
        },
        {
            "first_name": "Ava",
            "last_name": "Kim",
            "score": 10,
            "track": "Last Night"
        }
    ]
    # Sort friends list by descending score
    friends.sort(key=lambda x: x['score'], reverse=True)
    # Code
    return render_template("home.html", username=username, friends=friends)


# Comparison Page
@app.route("/compare", methods=["POST", "GET"])
@login_required
def compare():
    # Testcase
    username = current_user.username
    friend_username = "Chris"
    comparison_score = 80
    artists = [
        {
            "name": "Drake",
            "genre": "Hip-Hop/Rap"
        },
        {
            "name": "Olivia Rodrigo",
            "genre": "Pop"
        },
        {
            "name": "The Weeknd",
            "genre": "Dance/Electronic"
        },
        {
            "name": "Taylor Swift",
            "genre": "Pop"
        },
        {
            "name": "Morgan Wallen",
            "genre": "Country"
        }
    ]
    tracks = [
        {
            "name": "Flowers",
            "artist": "Miley Cyrus"
        },
        {
            "name": "Kill Bill",
            "artist": "SZA"
        },
        {
            "name": "Boy's A Liar, Pt. 2",
            "artist": "PinkPantheress & Ice Spice"
        },
        {
            "name": "Creepin'",
            "artist": "Metro Boomin, The Weeknd & 21 Savage"
        },
        {
            "name": "Last Night",
            "artist": "Morgan Wallen"
        }
    ]
    # Code
    return render_template(
        "compare.html",
        username=username,
        friend_username=friend_username,
        comparison_score=comparison_score,
        artists=artists,
        tracks=tracks
    )


# Callback route
@app.route("/callback", methods=["POST", "GET"])
@login_required
def callback():
    pass
