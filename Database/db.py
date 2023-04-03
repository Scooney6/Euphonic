import mysql.connector
from Config.config import configsql


# function to be used for creating new database connections
def connect():
    params = configsql()
    return mysql.connector.connect(**params)


# an example function for a function that returns all usernames from a table: Users
# Note: using the "with connect():" syntax creates a db connection that will automatically be destroyed
# after the return statement
def getUsers():
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT Username FROM User")
        return cur.fetchall()

def getUser(username):
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT Username FROM User WHERE Username = %s", (username,))
        user = cur.fetchone()
        return user[0] if user else None

def authorize(username, password):
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT Username FROM User WHERE Username = %s AND Password = %s", (username, password))
        user = cur.fetchone()
        if user:
            return True
        else:
            return False

def getToken(username):
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT Spotifytoken FROM User WHERE Username = %s", (username,))
        token = cur.fetchone()
        return token[0] if token else None

def adduser(username, password):
    with connect() as con:
        cur = con.cursor()
        cur.execute("INSERT INTO User (Username, Password) VALUES (%s, %s)", (username, password))
        con.commit()
        return True

def updateToken(username, token):
    with connect() as con:
        cur = con.cursor()
        cur.execute("UPDATE User SET Spotifytoken = %s WHERE Username = %s", (token, username))
        con.commit()
        return True
