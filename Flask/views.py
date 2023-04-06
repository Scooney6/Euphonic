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
    # If the login form was filled out:
    if 'logusername' in request.form and 'logpass' in request.form:
        username = request.form['logusername']
        password = request.form['logpass']
        # If the user pass provided are correct in the database:
        if authenticate(username, password):
            # Set session variables
            session['username'] = username
            session['uid'] = getUID(username)[0]
            session['loggedin'] = True

            # Check if the user has a stored spotify ID, if they do that means they have successfully authorized us
            # through spotify and they can proceed. Otherwise, send them to the authorization redirect.
            if not getSpotifyID(session['uid'])[0]:
                return redirect('https://accounts.spotify.com/authorize?' + getAuthRedirect())

            # Set token related session variables
            t = getToken(session['uid'])
            session['token'] = t[0]
            session['refresh_token'] = t[1]
            session['token_expiration'] = t[2]

            # Now we can let them access the home page
            return redirect("home")
    else:
        return render_template("index.html", msg='Username and Password Required')


# Handle for register form submission
@app.route('/register', methods=["POST"])
def register():
    # If the register form is filled out:
    if 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        # If the username is already taken:
        if getUsername(username):
            msg = 'Username taken'
            return render_template("index.html", msg=msg)
        else:
            # Add user to the database (NOTE: We don't yet have the spotify ID)
            addUser(username, password)

            # Create Session variable for this user so we know they are logged in
            session['loggedin'] = True
            session['uid'] = getUID(username)[0]
            session['username'] = username

            # Redirect the user to Spotify authorization
            return redirect('https://accounts.spotify.com/authorize?' + getAuthRedirect())
    else:
        msg = 'Username and Password Required'
        return render_template("index.html", msg=msg)


# Logout
@app.route('/logout', methods=['POST'])
def logout():
    # Clear session variable and send to index
    session.clear()
    return redirect('/')


# Home Page
@app.route("/home", methods=["POST", "GET"])
def home():
    # If the user is logged in
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
    # Get the code and state spotify gave us
    code = request.args.get('code')
    state = request.args.get('state')

    # Now so many things have to happen it's a miracle this works.
    # First we check if Spotify gave us a State and if the user denied authorization.
    # If those things are fine we can try to get the user's access token.
    # If that works we can check if a user has already registered with this spotify account.
    # Finally if everything checks out, add the token to the database.
    if not state or 'error' in request.args:
        session.clear()
        return render_template("index.html", msg="Error with Spotify Authorization.")
    if not getFirstToken(session, code):
        session.clear()
        return render_template("index.html", msg="Error With Spotify API")
    if not getFirstSpotifyID(session):
        session.clear()
        return render_template("index.html", msg="You can't register a spotify account to multiple accounts!")
    addToken(session['token'], session['refresh_token'], session['token_expiration'], session['uid'])
    return redirect('home')
