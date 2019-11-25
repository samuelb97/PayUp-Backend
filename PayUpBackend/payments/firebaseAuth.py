import pyrebase
from flask import Flask, jsonify, Blueprint, redirect, render_template, request, url_for
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, 
    get_jwt_identity, get_jwt_claims
)
from datetime import timedelta

firebaseAuth = Blueprint('firebaseAuth', __name__)

class UserObject:
    def __init__(self, name, id):
        self.name = name
        self.id = id

class Firebase:
    def __init__(self):
        self.config = {
            "apiKey": "AIzaSyAKoRVwuV9nL2izlKh0Yxz49OgPN4M5d3I",
            "authDomain": "payupelite.firebaseapp.com",
            "databaseURL": "https://payupelite.firebaseio.com",
            "storageBucket": "payupelite.appspot.com",
        }
        self.firebase = pyrebase.initialize_app(self.config)
        self.Auth = self.firebase.auth()
        self.user = None

    def auth(self, email, password):
        try:
            self.user = self.Auth.sign_in_with_email_and_password(email, password)
            return self.user
        except:
            return -1

firebase = Firebase()

@firebaseAuth.route('/login', methods=['POST'])
def login():
    print("Login")
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    params = request.get_json()
    username = params.get('username', None)
    password = params.get('password', None)

    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    fbUser = firebase.auth(username, password)

    if fbUser == -1:
        return jsonify({"msg": "Error Firebase Login"}), 400

    userId = fbUser["localId"]
    user = UserObject(name=username, id=userId)

    access_token = create_access_token(identity = user, expires_delta = timedelta(days = 1))
    ret = {'access_token': access_token}
    
    return jsonify(ret), 200
