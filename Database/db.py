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

# getScore - takes username, returns score
def getScore(username):
    with connect() as con:
        cur = con.cursor()

        # get userid using username from User Table
        # comparison table (has score column) does not have username column
        # comparison table has a userid1 column
        stmt1 = "SELECT userid FROM User WHERE username = %s"
        val1 = (username)
        cur.execute(stmt1, val1)
        uID = cur.fetchone()

        # in this query, a user's score is the sum of the scores associated
        # with the user's userid
        # result is the Score Sum 
        stmt2 = "SELECT SUM(Score) FROM Comparison WHERE userid1 = %s"
        val2 = uID
        cur.execute(stmt2, val2)
        result = cur.fetchone

        return result
    
# updateScore - takes 2 usernames and score
def updateScore(username, fUsername, score):
    with connect() as con:
        cur = con.cursor()
        
        # gets the userID of user because Comparison userId, not username
        stmt1 = "SELECT userid FROM User WHERE username = %s"
        val1 = (username)
        cur.execute(stmt1, val1)
        uID = cur.fetchone()

        # gets the userID of friend because Comparison userId, not username
        stmt2 = "SELECT userid FROM User WHERE username = %s"
        val2 = (fUsername)
        cur.execute(stmt2, val2)
        fID = cur.fetchone()

        # updates the score using adjacent colums
        stmt3 = "UPDATE Comparison SET Score = %s WHERE userid1 = %s AND userid2 = %s"
        val3 = (score, uID, fID)
        cur.execute(stmt3, val3)
        con.commit()

        # destroys db connection
        return True

# getFriends - takes username, returns all list of friends
def getFriends(username):
    with connect() as con:
        cur = con.cursor()

        # uses Friend Table
        # selects the entire username column and returns it
        sql = "SELECT username FROM Friend"
        cur.execute(sql)

        return cur.fetchall()

# addFriend - takes username of user and username of friend   
def addFriend(username, fUsername):
    with connect() as con:
        cur = con.cursor()

        # gets the userID of user because Comparison userId, not username
        stmt1 = "SELECT userid FROM User WHERE username = %s"
        val1 = (username)
        cur.execute(stmt1, val1)
        uID = cur.fetchone()

        # gets the userID of friend because Comparison userId, not username
        stmt2 = "SELECT userid FROM User WHERE username = %s"
        val2 = (fUsername)
        cur.execute(stmt2, val2)
        fID = cur.fetchone()
        
        # inserts into the Adds Table
        # Adds table is referenced by tables User and Friend
        # linked by a forign keys that are not null
        sql = "INSERT INTO Adds (user, friend) VALUES (%s, %s)"
        val = (uID, fID)
        cur.execute(sql, val)
        con.commit()

        return True
