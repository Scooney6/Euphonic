import secrets
import string
import time
from functools import lru_cache

import requests

from urllib.parse import urlencode
from requests.auth import HTTPBasicAuth
from Config.config import spotifyAuthParams
from Database.db import *


# Function to get the token for a user for the first time
def getFirstToken(session, code):
    # build request for user token
    params = spotifyAuthParams()
    url = 'https://accounts.spotify.com/api/token'
    data = {'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': params['redirect_uri']}
    # Make the post request
    response = requests.post(url, auth=HTTPBasicAuth(params['client_id'], params['client_secret']), data=data)
    # If the request was successful:
    if response.status_code == 200:
        # Set session variables
        r = response.json()
        session['token'] = r['access_token']
        session['refresh_token'] = r['refresh_token']
        session['token_expiration'] = time.time() + r['expires_in']

        return True
    else:
        return False


# Function to build the spotify redirect URL
def getAuthRedirect():
    # Build spotify authorization redirect url
    params = spotifyAuthParams()
    # Create a random state key that spotify will send back to us
    state_key = ''.join(
        secrets.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for i in range(16))
    query_params = {'client_id': params['client_id'],
                    'response_type': 'code',
                    'redirect_uri': params['redirect_uri'],
                    'state': state_key,
                    'scope': params['scope'],
                    'show_dialog': True}
    return urlencode(query_params)


# Function to refresh and expired token
def refreshToken(r_token):
    params = spotifyAuthParams()
    url = 'https://accounts.spotify.com/api/token'
    data = {'grant_type': 'refresh_token',
            'refresh_token': r_token}
    response = requests.post(url, auth=HTTPBasicAuth(params['client_id'], params['client_secret']), data=data)
    if response.status_code == 200:
        return response.json()
    else:
        return None


# Function to check the status of a token and refresh it if need be
def checkUserTokenStatus(session):
    if time.time() > session['token_expiration']:
        payload = refreshToken(session['refresh_token'])
        if payload:
            session['token'] = payload['access_token']
            session['refresh_token'] = payload['refresh_token']
            session['token_expiration'] = time.time() + payload['expires_in']
            updateToken(payload['access_token'], payload['refresh_token'], session['token_expiration'], session['uid'])
    else:
        return None
    return "Success"


def checkTokenStatus(uid):
    token_info = getToken(uid)
    if time.time() > token_info[2]:
        payload = refreshToken(token_info[1])
        if payload:
            updateToken(payload['access_token'], payload['refresh_token'], time.time() + payload['expires_in'], uid)
    else:
        return None
    return "Success"


# Function to build and make a get request to an API endpoint
def makeUserGetRequest(session, url, params={}):
    headers = {"Authorization": "Bearer {}".format(session['token'])}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401 and checkUserTokenStatus(session) is not None:
        return makeUserGetRequest(session, url, params)
    else:
        return None


# Function to get the Spotify ID for the first time
def getFirstSpotifyID(session):
    r = makeUserGetRequest(session, "https://api.spotify.com/v1/me", {})
    if r is not None and not getSpotifyID(session['uid'])[0]:
        addSpotifyID(session['uid'], r['id'])
        return True
    else:
        return False


@lru_cache()
def getLastListened(uid):
    headers = {"Authorization": "Bearer {}".format(getToken(uid)[0])}
    response = requests.get("https://api.spotify.com/v1/me/player/recently-played", headers=headers, params={"limit": 1})
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401 and checkTokenStatus(uid) is not None:
        return getLastListened(uid)
    else:
        return None
