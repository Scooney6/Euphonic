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
    # Code
    return render_template("home.html", username=username)


# Comparison Page
@app.route("/compare", methods=["POST", "GET"])
def compare():
    # Testcase
    username = "John"
    friendsUsername = "Chris"
    comparison_score = 80
    artist_1 = "Drake"
    artist_2 = "Olivia Rodrigo"
    artist_3 = "The Weeknd"
    artist_4 = "Taylor Swift"
    artist_5 = "Morgan Wallen"
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
        artist_2=artist_2,
        artist_3=artist_3,
        artist_4=artist_4,
        artist_5=artist_5,
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
