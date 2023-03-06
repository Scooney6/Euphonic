from flask import render_template
# from flask_login import logout_user
from Flask import app


# Landing Page
@app.route("/", methods=["POST", "GET"])
def index():
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
    # Testcase
    username = "John"
    friendsUsername = "Chris"
    comparison_score = 80
    artist_1 = "Drake"
    artistGenre_1 = "Hip-Hop/Rap"
    artist_2 = "Olivia Rodrigo"
    artistGenre_2 = "Pop"
    artist_3 = "The Weeknd"
    artistGenre_3 = "Dance/Electronic"
    artist_4 = "Taylor Swift"
    artistGenre_4 = "Pop"
    artist_5 = "Morgan Wallen"
    artistGenre_5 = "Country"
    track_1 = "Flowers"
    trackArtist_1 = "Miley Cyrus"
    track_2 = "Kill Bill"
    trackArtist_2 = "SZA"
    track_3 = "Boy's A Liar, Pt. 2"
    trackArtist_3 = "PinkPantheress & Ice Spice"
    track_4 = "Creepin'"
    trackArtist_4 = "Metro Boomin, The Weeknd & 21 Savage"
    track_5 = "Last Night"
    trackArtist_5 = "Morgan Wallen"

    # Code
    return render_template(
        "compare.html",
        username=username,
        comparison_score=comparison_score,
        friendsUsername=friendsUsername,
        artist_1=artist_1,        
        artistGenre_1 = artistGenre_1,
        artist_2=artist_2,
        artistGenre_2 = artistGenre_2,
        artist_3=artist_3,
        artistGenre_3 = artistGenre_3,
        artist_4=artist_4,
        artistGenre_4 = artistGenre_4,
        artist_5=artist_5,
        artistGenre_5 = artistGenre_5,
        track_1=track_1,
        trackArtist_1=trackArtist_1,
        track_2=track_2,
        trackArtist_2=trackArtist_2,
        track_3=track_3,
        trackArtist_3=trackArtist_3,
        track_4=track_4,
        trackArtist_4=trackArtist_4,
        track_5=track_5,
        trackArtist_5=trackArtist_5
    )
