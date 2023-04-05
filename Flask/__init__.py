from flask import Flask
from Config.config import configflask


# Initialize the flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = configflask()["secret_key"]


# THIS MUST COME AFTER the Flask application has been initialized so that the app can add the routes from views.py
from Flask.views import *
