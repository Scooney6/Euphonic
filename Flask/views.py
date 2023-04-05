from flask import render_template, redirect, request, session

from API.spotify import *
from Database.db import *
from Flask import app


# Login Page
@app.route("/", methods=["POST", "GET"])
def index():
    services = ['Spotify', 'More to come!']
    return render_template('index.html', services=services)


# Handle for login form submission
@app.route('/login', methods=["POST"])
def login():
    if 'Username' in request.form and 'Password' in request.form:
        username = request.form['Username']
        password = request.form['Password']
        if authenticate(username, password):
            session['username'] = username
            session['uid'] = getUID(username)
            session['loggedin'] = True
            return redirect("home")
    else:
        return render_template("index.html", msg='Username and Password Required')


# Handle for register form submission
@app.route('/register', methods=["POST"])
def register():
    if 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        if getUser(username):
            msg = 'Username taken'
            return render_template("index.html", msg=msg)
        else:
            # TODO implement addUser() in db.py
            # addUser(username, password)

            # Create Session variable for this user so we know they are logged in
            session['loggedin'] = True
            session['uid'] = getUID(username)
            session['username'] = username

            return redirect('https://accounts.spotify.com/authorize?' + getAuthRedirect())
    else:
        msg = 'Username and Password Required'
        return render_template("index.html", msg=msg)


# Logout
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect('/')


# Home Page
@app.route("/home", methods=["POST", "GET"])
def home():
    if 'loggedin' in session:
        print(makeGetRequest(session, 'https://api.spotify.com/v1/me/top/tracks', {'limit': '5'}))
        # Testcase
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
        return render_template("home.html", username=session['username'], friends=friends)
    else:
        return redirect("/")


# Comparison Page
@app.route("/compare", methods=["POST", "GET"])
def compare():
    # Testcase
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
        username=session['username'],
        friend_username=friend_username,
        comparison_score=comparison_score,
        artists=artists,
        tracks=tracks
    )


# Callback route for spotify authorization
@app.route("/callback", methods=["POST", "GET"])
def callback():
    # get the code and state spotify gave us
    code = request.args.get('code')
    state = request.args.get('state')
    if not state:
        return render_template("index.html", msg="Error with Spotify Authentication.")
    else:
        if getFirstToken(session, code):
            return redirect("home")
        else:
            return render_template("index.html", msg="Error with spotify authorization")