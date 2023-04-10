import mysql.connector
from Config.config import configsql


# function to be used for creating new database connections
def connect():
    params = configsql()
    return mysql.connector.connect(**params)


def getUsername(username):
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT Username FROM User WHERE Username LIKE %s", (username,))
        val = cur.fetchone()
        return val[0] if val is not None else None


def getUsernameByID(uid):
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT Username FROM User WHERE idUser LIKE %s", (uid,))
        val = cur.fetchone()
        return val[0] if val is not None else None


def getSpotifyID(uid):
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT idSpotify FROM User WHERE idUser LIKE %s", (uid,))
        val = cur.fetchone()
        return val[0] if val is not None else None


def addSpotifyID(uid, sid):
    with connect() as con:
        cur = con.cursor()
        cur.execute("UPDATE User SET idSpotify = %s WHERE idUser = %s", (sid, uid))
        con.commit()


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
        val = cur.fetchone()
        return val[0] if val is not None else None


def getToken(idUser):
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT token, refresh_token, expires_at FROM Token WHERE idUser = %s", (idUser,))
        return cur.fetchone()


def addUser(username, password):
    with connect() as con:
        cur = con.cursor()
        cur.execute("INSERT INTO User (Username, Password) VALUES (%s, %s)", (username, password))
        con.commit()
        return True


def addToken(token, refresh_token, expires_at, idUser):
    with connect() as con:
        cur = con.cursor()
        cur.execute("INSERT INTO Token (idUser, token, refresh_token, expires_at) VALUES (%s, %s, %s, %s)", (idUser, token, refresh_token, expires_at))
        con.commit()
        return True


def updateTokenNewRefresh(token, refresh_token, expires_at, idUser):
    with connect() as con:
        cur = con.cursor()
        cur.execute("UPDATE Token SET token = %s, refresh_token = %s, expires_at = %s WHERE idUser = %s", (token, refresh_token, expires_at, idUser))
        con.commit()
        return True


def updateToken(token, expires_at, idUser):
    with connect() as con:
        cur = con.cursor()
        cur.execute("UPDATE Token SET token = %s, expires_at = %s WHERE idUser = %s", (token, expires_at, idUser))
        con.commit()
        return True


# getScore - takes username, returns score
def getScore(uid, fid):
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT Score FROM Comparison WHERE (userid1 = %s and userid2 = %s) OR (userid1 = %s and userid2 = %s)", (uid, fid, fid, uid))
        val = cur.fetchone()
        return val[0] if val is not None else None


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
def getFriends(uid):
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT frienduser_id FROM Friend WHERE useruser_id = %s", (uid,))
        temp = cur.fetchall()
        return [item for t in temp for item in t]


# addFriend - takes username of user and username of friend   
def addFriend(uid, friend_username):
    with connect() as con:
        cur = con.cursor()

        # gets the userID of user because Comparison userId, not username
        cur.execute("SELECT idUser FROM User WHERE username = %s", (friend_username,))
        fid = cur.fetchone()[0]

        cur.execute("SELECT useruser_id, frienduser_id FROM Friend WHERE useruser_id = %s AND frienduser_id = %s",
                    (uid, fid))
        friend_exists = cur.fetchone()

        if friend_exists is None:
            # inserts into the Adds Table
            # Adds table is referenced by tables User and Friend
            # linked by a forign keys that are not null
            cur.execute("INSERT INTO Friend (useruser_id, frienduser_id) VALUES (%s, %s)", (uid, fid))
            con.commit()
        return True


# deleteFriend - takes username of user and username of friend
def deleteFriend(uid, friend_username):
    with connect() as con:
        cur = con.cursor()

        # gets the userID of user because Comparison userId, not username
        cur.execute("SELECT idUser FROM User WHERE username = %s",
                    (friend_username,))
        fid = cur.fetchone()[0]

        # deletes from the Adds Table
        cur.execute(
            "DELETE FROM Friend WHERE useruser_id = %s AND frienduser_id = %s", (uid, fid))
        con.commit()

        return True
