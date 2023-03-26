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
        cur.execute("SELECT Username FROM Users")
        return cur.fetchall()