from flask import Flask
from flask_login import LoginManager
from Config.config import configflask


# Initialize the flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = configflask()["secret_key"]


# Configure Flask login manager
login_manager = LoginManager(app)


# THIS MUST COME AFTER the Flask application has been initialized so that the app can add the routes from views.py
from Flask.views import *


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))