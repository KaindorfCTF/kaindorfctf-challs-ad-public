from __future__ import annotations
import os

from flask import Flask, request, jsonify
from model import db
from model.User import User
from model.Message import Message

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.getenv('PG_User', 'postgres')}:"
    f"{os.getenv('PG_Password', 'postgres')}"
    f"@{os.getenv('PG_Host', '127.0.0.1')}:5432/"
    f"{os.getenv('PG_DB', 'test')}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# Register endpoint
@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    password = request.json['password']

    if User.does_exist(username):
        return "1", 409

    User.add(username, password)
    return "0", 201


# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']

    if not User.is_authenticated(username, password):
        return "1", 401

    return "0", 200


# Set message endpoint
@app.route('/setmessage', methods=['POST'])
def setmessage():
    username = request.json['username']
    message = request.json['message']

    user_id = User.get_id(username)
    if user_id is None:
        return "1", 404

    if not Message.add_for_user(user_id, message):
        return "1", 400

    return "0", 201


# Get messages endpoint
@app.route('/getmessages', methods=['POST'])
def getmessages():
    username = request.json['username']
    is_admin = request.json.get('isadmin', 'False') == 'True'

    if is_admin:
        messages = Message.get_last_messages(100)
    else:
        user_id = User.get_id(username)
        if user_id is None:
            return "1", 404
        messages = Message.get_last_messages_from_user(user_id, 100)

    return messages, 200


# Get registered users endpoint
@app.route('/getusers', methods=['GET'])
def getusers():
    users = User.get_registered_users(100)
    return users, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
