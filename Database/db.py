import mysql.connector
from Config.config import configsql


# function to be used for creating new database connections
def connect():
    params = configsql()
    return mysql.connector.connect(**params)


# an example function for a function that returns all usernames from a table: Users
# Note: using the "with connect():" syntax creates a db connection that will automatically be destroyed
# after the return statement
def getUser(username):
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT Username FROM User WHERE Username LIKE %s", (username,))
        return cur.fetchone()


def authenticate(username, password):
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT Username FROM User WHERE Username = %s AND Password = %s", (username, password))
        user = cur.fetchone()
        if user:
            return True
        else:
            return False


def getUID(username):
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT idUser FROM User WHERE Username = %s ", (username,))
        return cur.fetchone()
