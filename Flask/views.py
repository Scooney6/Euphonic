import itertools
from collections import Counter

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
        friend_data = {}
        friend_ids = getFriends(session['uid'])
        for fid in friend_ids:
            friend_data[str(fid)] = {}
            friend_data[str(fid)]['username'] = getUsernameByID(fid)
            track = makeGetRequest(fid, "https://api.spotify.com/v1/me/player/recently-played", params={"limit": 1})
            if track is not None:
                friend_data[str(fid)]['track'] = track['items'][0]['track']['name']
                friend_data[str(fid)]['track_href'] = track['items'][0]['track']['external_urls']['spotify']
            else:
                friend_data[str(fid)]['track'] = "Unavailable"
            score = getScore(session['uid'], str(fid))
            if score is not None:
                friend_data[str(fid)]['score'] = score
            else:
                friend_data[str(fid)]['score'] = 'N/A'
        # Sort friends list by descending score NOT SURE IF THIS WORKS
        sorted(friend_data, key=lambda x: friend_data[x]['score'], reverse=True)
        leaderboard = {}
        scores = getTopScores()
        for i in range(len(scores)):
            leaderboard[str(i)] = {}
            leaderboard[str(i)]['user1'] = getUsernameByID(scores[i][0])
            leaderboard[str(i)]['user2'] = getUsernameByID(scores[i][1])
            leaderboard[str(i)]['score'] = scores[i][2]
        return render_template("home.html", username=session['username'], friend_data=friend_data,
                               leaderboard=leaderboard)
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
                session['error'] = "That user must link their Spotify first"
                return redirect('../home')
        else:
            session['error'] = "Username not found"
            return redirect('../home')


# deleteFriendRoute - deletes a friend from a user's friend list
@app.route('/delete_friend/<friend_username>', methods=["GET"])
def deleteFriendRoute(friend_username):
    if getUsername(friend_username):
        deleteFriend(session['uid'], friend_username)
        return redirect('../home')
    else:
        return redirect('../home')


@app.route('/compare_route/<friend_username>', methods=["GET"])
def compareRoute(friend_username):
    if getUsername(friend_username):
        if session['username'] < friend_username:
            return redirect('../compare/' + session['username'] + '/' + friend_username)
        else:
            return redirect('../compare/' + friend_username + '/' + session['username'])


# Comparison Page
@app.route("/compare/<user1>/<user2>", methods=["GET"])
def compare(user1, user2):
    u1id = getUID(user1)
    u2id = getUID(user2)

    user1_top_tracks = makeGetRequest(u1id, "https://api.spotify.com/v1/me/top/tracks", params={'limit': 50})
    user2_top_tracks = makeGetRequest(u2id, "https://api.spotify.com/v1/me/top/tracks", params={'limit': 50})
    shared_tracks = []
    if user1_top_tracks is not None and user2_top_tracks is not None:
        for track in user1_top_tracks['items']:
            for track2 in user2_top_tracks['items']:
                if track['id'] == track2['id']:
                    shared_tracks.append({
                        'name': track['name'],
                        'href': track['external_urls']['spotify']
                    })
    else:
        pass
    print("tracks in common: " + str(shared_tracks))

    user1_top_artists = makeGetRequest(u1id, "https://api.spotify.com/v1/me/top/artists", params={'limit': 50})
    user2_top_artists = makeGetRequest(u2id, "https://api.spotify.com/v1/me/top/artists", params={'limit': 50})
    shared_artists = []
    user1_genres = []
    user2_genres = []
    if user1_top_artists is not None and user2_top_artists is not None:
        for artist in user1_top_artists['items']:
            user1_genres.append(artist['genres'])
            for artist2 in user2_top_artists['items']:
                user2_genres.append(artist2['genres'])
                if artist['id'] == artist2['id']:
                    shared_artists.append({
                        'name': artist['name'],
                        'href': artist['external_urls']['spotify']
                    })
    else:
        pass
    print("artists in common: " + str(shared_artists))
    user1_genre_freq = {}
    for genre in itertools.chain.from_iterable(user1_genres):
        if genre in user1_genre_freq.keys():
            user1_genre_freq[genre] += 1
        else:
            user1_genre_freq[genre] = 1
    user2_genre_freq = {}
    for genre in itertools.chain.from_iterable(user2_genres):
        if genre in user2_genre_freq.keys():
            user2_genre_freq[genre] += 1
        else:
            user2_genre_freq[genre] = 1

    shared_genres = {}
    for genre in user1_genre_freq:
        for genre2 in user2_genre_freq:
            if genre == genre2:
                shared_genres[genre] = (user1_genre_freq[genre] + user2_genre_freq[genre]) - abs(user1_genre_freq[genre] - user2_genre_freq[genre])

    shared_genres = dict(sorted(shared_genres.items(), key=lambda x:x[1], reverse=True))
    shared_genres = list(shared_genres.keys())[0:5]
    print(str(shared_genres))
    score = len(shared_artists) + len(shared_tracks)
    updateScore(u1id, u2id, score)
    return render_template("compare.html", user1=user1, user2=user2, shared_artists=shared_artists,
                           shared_genres=shared_genres, score=score)


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
    id_check = getFirstSpotifyID(session['uid'], t)
    if id_check == "Duplicate ID":
        session.clear()
        return render_template("index.html", msg="You can't register a spotify account to multiple accounts!")
    elif id_check == "Failed to retrieve Spotify ID":
        session.clear()
        return render_template("index.html", msg="Error with Spotify Authorization")
    addToken(t['access_token'], t['refresh_token'], time.time() + t['expires_in'], session['uid'])
    return redirect('home')
