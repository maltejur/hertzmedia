from flask import Flask, request, make_response, jsonify, json, abort, g
from flask_restful import Api, Resource, reqparse, fields, marshal
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS
from flaskext.mysql import MySQL
from passlib.context import CryptContext
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
import uuid
import jwt
import datetime
import secrets
import os
import string
import random
import re
import base64
import time

time.sleep(2)  # Wait for mysql to start

app = Flask(__name__)
CORS(app)
auth = HTTPBasicAuth()
api = Api(app)
cr = CryptContext(schemes=["sha256_crypt"])


def config(app):
    with open("./hertzmedia.config") as config:
        for line in config:
            configName = line[0:line.index("=")].strip()
            config = line[line.index("=") + 1: len(line)].strip()
            if (config.startswith("(int)")):
                config = config[5:]
                app.config[configName] = int(config)
            else:
                app.config[configName] = config


config(app)

db = MySQL()

db.init_app(app)

# requestParser setup
postParser = reqparse.RequestParser()
postParser.add_argument(
    "title", type=str, help="the title 20 letters max", required=True)
postParser.add_argument(
    "text", type=str, help="the posted text", required=True)
postParser.add_argument("file", type=str, help="optional file", required=False)
allowUserParser = reqparse.RequestParser()
allowUserParser.add_argument("username", type=str, required=True)
allowUserParser.add_argument("classname", type=str, required=True)
loginParser = reqparse.RequestParser()
loginParser.add_argument("username", type=str, required=True)
loginParser.add_argument("password", type=str, required=True)

subjectMap = {}
activeUser = None


def setSubjectMap(subjectMap):
    connection = db.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM subjects")
    subjectList = cursor.fetchall()
    subjectMap.clear()
    subjectMap[None] = ""
    for subject in subjectList:
        subjectMap[subject[0]] = subject[1]


setSubjectMap(subjectMap)


def generate_token(json, expiration=None):
    s = Serializer(app.config["SECRET_KEY"], expires_in=expiration)
    token = s.dumps(json)
    return token


def verify_token(token):
    connection = db.connect()
    cursor = connection.cursor()
    s = Serializer(app.config["SECRET_KEY"])
    try:
        token = s.loads(token)
    except SignatureExpired:
        return None
    except BadSignature:
        return None
    cursor.execute("SELECT * FROM user WHERE id = " +
                   str(token["userId"]) + ";")
    data = cursor.fetchone()
    if (token["tokenId"] != data[5]):
        return None
    return data


def verify_user(username, password):
    connection = db.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM user WHERE name = %s;", (username))
    user = cursor.fetchone()
    if (user is None):
        return None
    passwordHash = user[2]
    if cr.verify(password, passwordHash):
        return user
    return None


def hashCrypt(password):
    return cr.hash(secret=password)


def readTimetable(id):
    connection = db.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT h1, h2, h3, h4, h5, h6, h7, h8, h9 FROM classes" +
                   " JOIN timetables ON classes.timetable_id = timetables.id" +
                   " JOIN timetable_days ON timetables.mo = timetable_days.id OR timetables.tu =" +
                   " timetable_days.id OR timetables.we = timetable_days.id OR timetables.th = timetable_days.id" +
                   " OR timetables.fr = timetable_days.id WHERE classes.classId = " + str(id) + ";")
    data = cursor.fetchall()
    newData = []
    for _ in data:
        newData.append([None] * len(data[0]))
    for i in range(len(data)):
        for j in range(len(data[i])):
            newData[i][j] = subjectMap.get(data[i][j])
    return newData


@app.route("/users/create", methods=["POST"])
def createUser():
    connection = db.connect()
    cursor = connection.cursor()
    json = request.json
    username = json.get("username")
    classname = json.get("classname")
    password = json.get("password")
    if username is None or password is None:
        abort(406)
    cursor.execute("SELECT * FROM allowedUsers JOIN classes ON allowedUsers.classId = classes.classId" +
                   " WHERE allowedUsers.name = %s AND classes.name = %s LIMIT 1;", (username, classname))
    out = cursor.fetchone()
    if (out is None):
        abort(403)
    id = out[0]
    cursor.execute("SELECT * FROM user WHERE name = %s LIMIT 1;", (username))
    if (cursor.fetchone() is not None):
        abort(409)

    hash = hashCrypt(password)

    if (type(out[3]) != int):
        exit()

    cursor.execute("INSERT INTO user(name, passwordHash, admin, classId)" +
                   "VALUE(%s, %s, " + str(out[3]) + ", " + str(out[2]) + ");", (username, hash))

    cursor.execute("DELETE FROM allowedUsers WHERE id = " + str(id) + ";")
    connection.commit()
    return {"info": "user successfully added"}


@app.route("/timetable", methods=["GET"])
@auth.login_required
def getTimetable():
    connection = db.connect()
    cursor = connection.cursor()
    userId = activeUser[4]
    classId = cursor.fetchone()
    data = readTimetable(userId)
    return {"data": {
            "mo": data[0],
            "tu": data[1],
            "we": data[2],
            "th": data[3],
            "fr": data[4]}}


@app.route("/login", methods=["POST"])
def login():
    return defaultLogin(600)


@app.route("/loginpermanent", methods=["POST"])
def loginpermanent():
    return defaultLogin(315360000)


def defaultLogin(expiration):
    connection = db.connect()
    cursor = connection.cursor()
    args = loginParser.parse_args()
    username = args["username"]
    password = args["password"]
    if (verify_user(username, password) is not None):
        cursor.execute(
            "SELECT id, lastTokenId FROM user WHERE name = %s;", (username))
        data = cursor.fetchone()
        userId = data[0]
        tokenId = data[1]
        if (data is None):
            abort(404)
        token = generate_token(
            {"userId": userId, "tokenId": tokenId}, expiration)
        return {"data": {"token": token.decode("ascii")}}
    abort(403)


@app.route("/expiretokens", methods=["GET"])
@auth.login_required
def expireTokens():
    print("expire Tokens")
    connection = db.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT lastTokenId FROM user WHERE id = " +
                   str(activeUser[0]) + ";")
    data = cursor.fetchone()
    tokenId = data[0] + 1
    cursor.execute("UPDATE user SET lastTokenId = " +
                   str(tokenId) + " WHERE id = " + str(activeUser[0]) + ";")
    connection.commit()
    return {"data": "logged out and dropped all tokens"}


@app.route("/au", methods=["POST"])
@auth.login_required
def allowUser():
    connection = db.connect()
    cursor = connection.cursor()
    args = allowUserParser.parse_args()
    username = args.get("username")
    className = args.get("classname")
    className = className.replace(":", "-")
    className = className.replace("_", "-")
    cursor.execute("SELECT classId FROM classes WHERE name = %s;", (className))
    classId = cursor.fetchone()
    if (classId is None or username is None or username == ""):
        abort(406)
    # check if person name and class combination is unique
    cursor.execute("SELECT allowedUsers.name, classes.name FROM allowedUsers " +
                   "JOIN classes ON allowedUsers.classId = classes.classId " +
                   "WHERE allowedUsers.name = %s AND classes.name = %s;",
                   (username, className))
    if (cursor.fetchone() is not None):
        abort(409)
    cursor.execute("SELECT user.name, classes.name FROM user " +
                   "JOIN classes ON user.classId = classes.classId " +
                   "WHERE user.name = %s AND classes.name = %s;",
                   (username, className))
    if (cursor.fetchone() is not None):
        abort(409)
    cursor.execute("INSERT INTO allowedUsers(name, classId) VALUE(%s, %s);",
                   (username, classId))
    connection.commit()
    return {"data": "user succesfully stored"}


@app.route("/posts/<string:name>/<int:amount>/<int:lastId>", methods=["GET"])
@auth.login_required
def getFromChannel(name, amount, lastId):
    connection = db.connect()
    cursor = connection.cursor()
    getLimit = 10
    cursor.execute("SELECT id FROM channels WHERE name = %s;", (name))
    target = cursor.fetchone()
    if (target is None):
        abort(404)
    id = target[0]
    if (amount > getLimit):
        amount = getLimit
    if (lastId == 0):
        cursor.execute("SELECT posts.id, title, text, posttime, writerId, data FROM posts" +
                       " LEFT JOIN resources ON resourceId = resources.id WHERE targetStreamId = " + str(id) +
                       " ORDER BY postTime DESC LIMIT " + str(amount) + ";")
    else:
        cursor.execute("SELECT posts.id, title, text, posttime, writerId, data FROM posts" +
                       " LEFT JOIN resources ON resourceId = resources.id WHERE posts.id < " + str(lastId) + " AND targetStreamId = " + str(id) +
                       " ORDER BY postTime DESC LIMIT " + str(amount) + ";")
    data = cursor.fetchmany(amount)
    data = list(data)
    for j in range(len(data)):
        cursor.execute("SELECT name FROM user WHERE id = " +
                       str(data[j][4]) + ";")
        file = data[j][5]
        if (file is not None):
            file = str(base64.standard_b64encode(data[j][5]))[2:-1]
        data[j] = {
            "id": data[j][0],
            "title": str(data[j][1]),
            "text": str(data[j][2]),
            "time": str(data[j][3]),
            "creator": cursor.fetchone()[0],
            "file": file
        }
    return {"data": data}


@app.route("/channels/name/<string:startsWith>")
@auth.login_required
def getChannelsByName(startsWith):
    connection = db.connect()
    cursor = connection.cursor()
    if (re.search("([a-z]|[A-Z]|[0-9]|[ öäüÖÄÜß])+", startsWith) is None):
        abort(400)
    cursor.execute(
        "SELECT name FROM channels WHERE (lower(name) LIKE '" + startsWith + "%') LIMIT 10;")
    data = cursor.fetchall()
    channels = []
    for c in data:
        channels.append(c[0])
    return {"data": channels}


@app.route("/posts/<string:name>/create", methods=["POST"])
@auth.login_required
def postOnChannel(name):
    connection = db.connect()
    cursor = connection.cursor()
    args = postParser.parse_args()
    title = args.get("title")
    text = args.get("text")
    if (title == ""):
        abort(400)
    if (len(title) > 128):
        title = title[0:125] + "..."
    if (len(text) > 2096):
        abort(400)
    cursor.execute("SELECT id, public FROM channels WHERE name = %s;", (name))
    target = cursor.fetchone()
    if (target is None):
        abort(404)
    id = target[0]
    public = target[1]
    if (not public):
        cursor.execute("SELECT * FROM channelConnections WHERE userId = " +
                       str(activeUser[0]) + " AND channelId = " + str(id) + ";")
        channelConneciton = cursor.fetchone()
        if (channelConneciton is None and activeUser[1] != app.config["ROOT"]):
            abort(405)
    res = args.get("file")
    resId = "NULL"
    if (res is not None):
        try:
            res = base64.b64decode(res)
        except:
            abort(400)
        cursor.execute("INSERT INTO resources(data) VALUES(x%s);", (res.hex()))
        cursor.execute("SELECT LAST_INSERT_ID();")
        resId = str(cursor.fetchone()[0])
    cursor.execute("INSERT INTO posts(writerId, targetStreamId, title, text, resourceId) " +
                   "VALUES (" + str(activeUser[0]) + ", " + str(id) + ", %s, %s, " + resId + ");", (title, text))
    connection.commit()
    return {"info": "data successfully Stored"}


@app.route("/channels/<path:channelInfo>", methods=["POST"])
@auth.login_required
def createChannel(channelInfo):
    connection = db.connect()
    cursor = connection.cursor()
    if (re.search("^(([a-z]|([A-Z]|([0-9]|[ öäüßÖÄÜ])))+)/((true)|(false))$", channelInfo) is None):
        abort(400)
    channelName = channelInfo[0:channelInfo.find("/")]
    isPublic = (channelInfo[channelInfo.find("/") + 1:])
    cursor.execute("SELECT * FROM channels WHERE name = %s;", (channelName))
    if (cursor.fetchone() is not None):
        abort(409)
    cursor.execute("INSERT INTO channels(creatorId, name, public) VALUES(" +
                   activeUser.id + ", %s, %s);", (channelName, isPublic))
    cursor.execute("INSERT INTO channelConnections(userId, channelId, admin) VALUES(" +
                   activeUser.id + ", LAST_INSERT_ID(), true)")
    return {"info": "data successfully Stored"}


@app.errorhandler(404)
def not_found(a):
    return make_response({"error": "404 Not found"}, 404)


@auth.verify_password
def verify_password(username, password):
    global activeUser
    user = verify_token(username)
    if (user is not None):
        activeUser = user
        return True
    activeUser = None
    return False


@app.errorhandler(403)
def unauthorited(a):
    return make_response({"error": "403 access denied"}, 403)


# run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
