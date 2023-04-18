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
            if not getSpotifyIDbyuID(session['uid']):
                return redirect('https://accounts.spotify.com/authorize?' + getAuthRedirect())

            # Now we can let them access the home page
            return redirect("home")
        else:
            return render_template("index.html", msg='Username or Password incorrect!')
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
    msg = None
    if 'error' in session:
        msg = session['error']
        session['error'] = None
        
    # If the user is logged in
    if 'loggedin' in session:
        friend_data = {}
        friend_request_data = {}
        friend_ids = getFriends(session['uid'])
        friend_request_ids = getFriendsRequests(session['uid'])
        for fid in friend_request_ids:
            friend_request_data[str(fid)] = {}
            friend_request_data[str(fid)]['username'] = getUsernameByID(fid)
        for fid in friend_ids:
            friend_data[str(fid)] = {}
            friend_data[str(fid)]['username'] = getUsernameByID(fid)
            track = makeGetRequest(
                fid, "https://api.spotify.com/v1/me/player/recently-played", params={"limit": 1})
            if track is not None:
                friend_data[str(
                    fid)]['track'] = track['items'][0]['track']['name']
                friend_data[str(
                    fid)]['track_href'] = track['items'][0]['track']['external_urls']['spotify']
            else:
                friend_data[str(fid)]['track'] = "Unavailable"
            score = getScore(session['uid'], str(fid))
            if score is not None:
                friend_data[str(fid)]['score'] = score
            else:
                friend_data[str(fid)]['score'] = 'N/A'
        leaderboard = {}
        scores = getTopScores()
        for i in range(len(scores)):
            leaderboard[str(i)] = {}
            leaderboard[str(i)]['user1'] = getUsernameByID(scores[i][0])
            leaderboard[str(i)]['user2'] = getUsernameByID(scores[i][1])
            leaderboard[str(i)]['score'] = scores[i][2]
        return render_template("home.html", username=session['username'], friend_data=friend_data, friend_request_data=friend_request_data,
                               leaderboard=leaderboard, msg=msg)
    else:
        return redirect("/")


@app.route('/add_friend')
def addFriendRoute():
    if 'friend_username' in request.args:
        friend_username = request.args['friend_username']
        if getUsername(friend_username):
            if getSpotifyIDbyuID(getUID(friend_username)):
                if getUID(friend_username) != session['uid']:
                    addFriend(session['uid'], friend_username)
                    return redirect('home')
                else:
                    session['error'] = "You can't add yourself as a friend. (Wouldn't that be nice!)"
                    return redirect('../home')
            else:
                session['error'] = "That user must link their Spotify first"
                return redirect('../home')
        else:
            session['error'] = "Username not found"
            return redirect('../home')
    else:
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
        if session['username'].lower() < friend_username.lower():
            return redirect('../compare/' + session['username'] + '/' + friend_username)
        else:
            return redirect('../compare/' + friend_username + '/' + session['username'])


def determineVibe(vibe_factors):
    maximum = max(vibe_factors, key=lambda y: abs(vibe_factors[y]))
    if maximum == 'valence':
        if vibe_factors['valence'] >= 0:
            return "Happy"
        else:
            return "Moody"
    elif maximum == 'danceability':
        if vibe_factors['danceability'] >= 0:
            return "Groovy"
        else:
            return "Chill"
    elif maximum == 'energy':
        if vibe_factors['energy'] >= 0:
            return "Explosive"
        else:
            return "Calm"
    else:
        return "Error :("


# Comparison Page
def percentChange(param, param1):
    return str(round((param - param1) / abs(param)))


@app.route("/compare/<user1>/<user2>", methods=["GET"])
def compare(user1, user2):
    u1id = getUID(user1)
    u2id = getUID(user2)

    
    msg = None
    if 'error' in session:
        msg = session['error']
        session['error'] = None

    # Get top 50 tracks for both users
    user1_top_tracks = makeGetRequest(
        u1id, "https://api.spotify.com/v1/me/top/tracks", params={'limit': 50})
    user2_top_tracks = makeGetRequest(
        u2id, "https://api.spotify.com/v1/me/top/tracks", params={'limit': 50})
    user1_trackids = []
    user2_trackids = []
    user1_vibe = "Error"
    user2_vibe = "Error"
    # Get the features for the top 50 tracks of both users
    if user1_top_tracks is not None and user2_top_tracks is not None:
        for track in user1_top_tracks['items']:
            user1_trackids.append(track['id'])
        for track in user2_top_tracks['items']:
            user2_trackids.append(track['id'])
        user1_trackids = ','.join(user1_trackids)
        user2_trackids = ','.join(user2_trackids)

        user1_track_features = makeGetRequest(u1id, "https://api.spotify.com/v1/audio-features",
                                              params={'ids': user1_trackids})
        user2_track_features = makeGetRequest(u2id, "https://api.spotify.com/v1/audio-features",
                                              params={'ids': user2_trackids})

        # Get the average of those features
        user1_avg_features = {'valence': 0.0, 'danceability': 0.0, 'energy': 0.0, 'acousticness': 0.0,
                              'instrumentalness': 0.0, 'liveness': 0.0}
        user2_avg_features = {'valence': 0.0, 'danceability': 0.0, 'energy': 0.0, 'acousticness': 0.0,
                              'instrumentalness': 0.0, 'liveness': 0.0}
        for track in user1_track_features['audio_features']:
            user1_avg_features['valence'] += track['valence']
            user1_avg_features['danceability'] += track['danceability']
            user1_avg_features['energy'] += track['energy']
            user1_avg_features['acousticness'] += track['acousticness']
            user1_avg_features['instrumentalness'] += track['instrumentalness']
            user1_avg_features['liveness'] += track['liveness']
        for track in user2_track_features['audio_features']:
            user2_avg_features['valence'] += track['valence']
            user2_avg_features['danceability'] += track['danceability']
            user2_avg_features['energy'] += track['energy']
            user2_avg_features['acousticness'] += track['acousticness']
            user2_avg_features['instrumentalness'] += track['instrumentalness']
            user1_avg_features['liveness'] += track['liveness']
        for feature in user1_avg_features.keys():
            user1_avg_features[feature] = user1_avg_features[feature] / 50
        for feature in user2_avg_features:
            user2_avg_features[feature] = user2_avg_features[feature] / 50

        user1_vibe_factors = {'valence': 0.0, 'danceability': 0.0, 'energy': 0.0}
        user2_vibe_factors = {'valence': 0.0, 'danceability': 0.0, 'energy': 0.0}
        for factor in user1_avg_features:
            user1_avg_features[factor] = user1_avg_features[factor] - 0.5
            if factor in user1_vibe_factors:
                user1_vibe_factors[factor] = user1_avg_features[factor]
        for factor in user2_avg_features:
            user2_avg_features[factor] = user2_avg_features[factor] - 0.5
            if factor in user2_vibe_factors:
                user2_vibe_factors[factor] = user2_avg_features[factor]
        user1_vibe = determineVibe(user1_vibe_factors)
        user2_vibe = determineVibe(user2_vibe_factors)
        sum_avg_feature_difference = 0
        music_similarity = {}

        if user1_avg_features['energy'] > user2_avg_features['energy']:
            music_similarity['energy_percent'] = user1 + " listens to " + percentChange(
                user1_avg_features['energy'],
                user2_avg_features['energy']) + "% more energetic music than " + user2
        else:
            music_similarity['energy_percent'] = user2 + " listens to " + percentChange(
                user2_avg_features['energy'],
                user1_avg_features['energy']) + "% more energetic music than " + user1

        if user1_avg_features['energy'] > 0 and user2_avg_features['energy'] > 0:
            music_similarity['energy'] = "You both listen to songs that have more energy than average."
        elif user1_avg_features['energy'] < 0 and user2_avg_features['energy'] < 0:
            music_similarity['energy'] = "You both listen to songs that have less energy than average."
        elif user1_avg_features['energy'] > 0 > user2_avg_features['energy']:
            music_similarity[
                'energy'] = user1 + " listens to songs that have more energy than average, but " + user2 + " listens to songs that have less energy than average."
        elif user1_avg_features['energy'] < 0 < user2_avg_features['energy']:
            music_similarity[
                'energy'] = user1 + " listens to songs that have less energy than average, but " + user2 + " listens to songs that have more energy than average."

        if user1_avg_features['valence'] > user2_avg_features['valence']:
            music_similarity['valence_percent'] = user1 + " listens to " + percentChange(
                user1_avg_features['valence'],
                user2_avg_features['valence']) + "% more happy music than " + user2
        else:
            music_similarity['valence_percent'] = user2 + " listens to " + percentChange(
                user2_avg_features['valence'],
                user1_avg_features['valence']) + "% more happy music than " + user1

        if user1_avg_features['valence'] > 0 and user2_avg_features['valence'] > 0:
            music_similarity['valence'] = "You both listen to more happy songs than sad songs."
        elif user1_avg_features['valence'] < 0 and user2_avg_features['valence'] < 0:
            music_similarity['valence'] = "You both listen to more sad songs than happy songs."
        elif user1_avg_features['valence'] > 0 > user2_avg_features['valence']:
            music_similarity[
                'valence'] = user1 + " listens to more happy songs, but " + user2 + " listens to more sad songs."
        elif user1_avg_features['valence'] < 0 < user2_avg_features['valence']:
            music_similarity[
                'valence'] = user1 + " listens to more sad songs, but " + user2 + "listens to more happy songs."

        if user1_avg_features['danceability'] > user2_avg_features['danceability']:
            music_similarity['danceability_percent'] = user1 + " listens to " + percentChange(
                user1_avg_features['danceability'],
                user2_avg_features['danceability']) + "% more danceable music than " + user2
        else:
            music_similarity['danceability_percent'] = user2 + " listens to " + percentChange(
                user2_avg_features['danceability'],
                user1_avg_features['danceability']) + "% more danceable music than " + user1

        if user1_avg_features['danceability'] > 0 and user2_avg_features['danceability'] > 0:
            music_similarity['danceability'] = "You both listen to songs that are more danceable than average."
        elif user1_avg_features['danceability'] < 0 and user2_avg_features['danceability'] < 0:
            music_similarity['danceability'] = "You both listen to songs that are less danceable than average."
        elif user1_avg_features['danceability'] > 0 > user2_avg_features['danceability']:
            music_similarity[
                'danceability'] = user1 + " listens to more danceable songs, but " + user2 + " listens to less danceable songs."
        elif user1_avg_features['danceability'] < 0 < user2_avg_features['danceability']:
            music_similarity[
                'danceability'] = user1 + " listens to less danceable songs, but " + user2 + "listens to more danceable songs."

        for factor in user1_avg_features:
            sum_avg_feature_difference += abs(user1_avg_features[factor] - user2_avg_features[factor])
        sum_avg_feature_difference = 1 - (sum_avg_feature_difference / len(user1_avg_features.keys()))
        music_similarity_score = 25 * sum_avg_feature_difference
    else:
        pass

    # Get shared top artists between the two users
    user1_top_artists = makeGetRequest(
        u1id, "https://api.spotify.com/v1/me/top/artists", params={'limit': 50})
    user2_top_artists = makeGetRequest(
        u2id, "https://api.spotify.com/v1/me/top/artists", params={'limit': 50})
    shared_artists = []
    user1_genres = []
    user2_genres = []
    if user1_top_artists is not None and user2_top_artists is not None:
        for artist in user1_top_artists['items']:
            user1_genres.append(artist['genres'])
            for artist2 in user2_top_artists['items']:
                if artist['id'] == artist2['id']:
                    shared_artists.append({
                        'name': artist['name'],
                        'href': artist['external_urls']['spotify']
                    })
        for artist2 in user2_top_artists['items']:
            user2_genres.append(artist2['genres'])
    else:
        pass
    if len(shared_artists) > 5:
        shared_artists = shared_artists[0:5]
    artist_score = len(shared_artists) * 4

    # Get shared genres between the two users
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
                shared_genres[genre] = (user1_genre_freq[genre] + user2_genre_freq[genre]) - abs(
                    user1_genre_freq[genre] - user2_genre_freq[genre])
    sum_shared_genres = 0
    for genre in shared_genres:
        sum_shared_genres += shared_genres[genre]
    normalized_sum_shared_genres = sum_shared_genres / (len(list(itertools.chain.from_iterable(user1_genres))) + len(
        list(itertools.chain.from_iterable(user2_genres))))
    genre_score = 50 * normalized_sum_shared_genres
    shared_genres = dict(sorted(shared_genres.items(), key=lambda x: x[1], reverse=True))
    shared_genres = dict(itertools.islice(shared_genres.items(), 5))
    shared_genres = list(shared_genres.keys())[0:5]

    if user2_vibe == user1_vibe:
        vibe_bonus = 10
        music_similarity['vibe'] = "You both share the same Vibe!"
    else:
        vibe_bonus = 0
        music_similarity['vibe'] = user1 + " and " + user2 + " have a different music vibe"

    print(
        "artist: " + str(artist_score) + " genre: " + str(genre_score) + " vibe: " + str(vibe_bonus) + " music " + str(
            music_similarity_score))
    score = round(artist_score + genre_score + vibe_bonus + music_similarity_score)
    updateScore(u1id, u2id, score)
    return render_template("compare.html", user1=user1, user2=user2, shared_artists=shared_artists,
                           shared_genres=shared_genres, score=score, user1_vibe=user1_vibe, user2_vibe=user2_vibe,
                           music_similarity=music_similarity, msg=msg)


# Callback route for spotify authorization
@app.route("/callback", methods=["POST", "GET"])
def callback():
    # Get the code and state spotify gave us
    code = request.args.get('code')
    state = request.args.get('state')

    # Check if the user's unique identifier is stored in the session dictionary
    if 'uid' not in session:
        session.clear()
        return render_template("index.html", msg="Error: User not authenticated.")

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
