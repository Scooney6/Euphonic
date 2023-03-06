from flask import render_template
# from flask_login import logout_user
from Flask import app


# Landing Page
@app.route("/", methods=["POST", "GET"])
def index():
    return render_template("index.html")

# LOGOUT
# @app.route('/logout', methods=['POST'])
# def logout():
#     logout_user()
#     return redirect(url_for('index'))



# Home Page
@app.route("/home", methods=["POST", "GET"])
def home():
    username = "John"  # Testcase
    return render_template("home.html", username=username)


# Comparison Page
@app.route("/compare", methods=["POST", "GET"])
def compare():
    # Testcase
    username = "John"
    friendsUsername = "Chris"
    comparison_score = 80
    # Code
    return render_template("compare.html", username=username, comparison_score=comparison_score, friendsUsername=friendsUsername)
