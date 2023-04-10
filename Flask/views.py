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
            session['uid'] = getUID(username)
            session['loggedin'] = True

            # Check if the user has a stored spotify ID, if they do that means they have successfully authorized us
            # through spotify and they can proceed. Otherwise, send them to the authorization redirect.
            if not getSpotifyID(session['uid']):
                return redirect('https://accounts.spotify.com/authorize?' + getAuthRedirect())

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
            session['uid'] = getUID(username)
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
        # print(makeGetRequest(session, 'https://api.spotify.com/v1/me/top/tracks', {'limit': '5'}))
        friend_data = {}
        friend_ids = getFriends(session['uid'])
        for fid in friend_ids:
            friend_data[str(fid)] = {}
            friend_data[str(fid)]['username'] = getUsernameByID(fid)
            track = makeGetRequest(fid, "https://api.spotify.com/v1/me/player/recently-played", params={"limit": 1})
            if track is not None:
                friend_data[str(fid)]['track'] = track
            else:
                friend_data[str(fid)]['track'] = "Unavailable"
            score = getScore(session['uid'], str(fid))
            if score is not None:
                friend_data[str(fid)]['score'] = score
            else:
                friend_data[str(fid)]['score'] = 'N/A'
        # Sort friends list by descending score NOT SURE IF THIS WORKS
        sorted(friend_data, key=lambda x: friend_data[x]['score'], reverse=True)
        print(friend_data)
        return render_template("home.html", username=session['username'], friend_data=friend_data)
    else:
        return redirect("/")


@app.route('/add_friend', methods=["POST"])
def addFriendRoute():
    if 'friend_username' in request.form:
        if getUsername(request.form['friend_username']):
            if getSpotifyID(getUID(request.form['friend_username'])):
                addFriend(session['uid'], request.form['friend_username'])
                return redirect('home')
            else:
                return render_template('home.html', msg='That user must link their Spotify first!')
        else:
            return render_template('home.html', msg="Username not found")


# deleteFriendRoute - deletes a friend from a user's friend list
@app.route('/delete_friend/<friend_username>', methods=["GET"])
def deleteFriendRoute(friend_username):
    if getUsername(friend_username):
        deleteFriend(session['uid'], friend_username)
        return redirect('../home')
    else:
        return redirect('../home')


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
    t = getFirstToken(session['uid'], code)
    if t is None:
        session.clear()
        return render_template("index.html", msg="Error With Spotify API")
    if not getFirstSpotifyID(session['uid'], t):
        session.clear()
        return render_template("index.html", msg="You can't register a spotify account to multiple accounts!")
    addToken(t['access_token'], t['refresh_token'], time.time() + t['expires_in'], session['uid'])
    return redirect('home')
