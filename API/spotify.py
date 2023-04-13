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
def getFirstToken(uid, code):
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
        print("Successfully retrieved first time token for user " + str(uid))
        return response.json()
    else:
        print("Failed to retrieve first time token for user " + str(uid))
        return None


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
        print("Failed to retrieve new token, code: " + str(response.status_code))
        return None


def checkTokenStatus(uid):
    print("Attempting to check token for user " + str(uid))
    token_info = getToken(uid)
    if time.time() > float(token_info[2]):
        print("Token for user " + str(uid) + " has expired. Attempting to retrieve new token")
        payload = refreshToken(token_info[1])
        if payload:
            print("Successfully retrieved new token for user: " + str(uid))
            if 'refresh_token' in payload:
                updateTokenNewRefresh(payload['access_token'], payload['refresh_token'], time.time() + payload['expires_in'], uid)
            else:
                updateToken(payload['access_token'], time.time() + payload['expires_in'], uid)
    else:
        return None
    return "Success"


def makeGetRequest(uid, url, params=None, t=None):
    if params is None:
        params = {}
    if t is None:
        headers = {"Authorization": "Bearer {}".format(getToken(uid)[0])}
    else:
        headers = {"Authorization": "Bearer {}".format(t['access_token'])}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        print("Successfully made a get request on behalf of user " + str(uid))
        return response.json()
    elif response.status_code == 401 and checkTokenStatus(uid) is not None:
        return makeGetRequest(uid, url, params)
    else:
        print("Failed to make a get request on behalf of user " + str(uid) + " for the url " + url)
        print("Error code: " + str(response.status_code))
        return None


# Function to get the Spotify ID for the first time
def getFirstSpotifyID(uid, t):
    r = makeGetRequest(uid, "https://api.spotify.com/v1/me", t=t)
    if r is not None:
        print("Successfully retrieved Spotify ID for user " + str(uid))
        if getSpotifyID(r['id']) is None:
            addSpotifyID(uid, r['id'])
            return "Success"
        else:
            print("User " + str(uid) + "'s Spotify ID is registered to another user")
            return "Duplicate ID"
    else:
        print("Failed to retrieve Spotify ID for user " + str(uid))
        return "Failed to retrieve Spotify ID"
