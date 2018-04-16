from pymongo import MongoClient
from config import CONFIG
import bcrypt


"""
Defines set of functions to communicate with DB of choice. Used in /flaskWebServer and /processingEngine .

DATABASE SPECIFICATIONS
    * NoSQL DB (most likely MongoDB)
        * User has id, username, tweet archive file, collection of tweets
            * Collection of tweets broken down by months
"""


def initialize_tweets_db():
    mongoClient = MongoClient(CONFIG['MONGODB_ADDR'])
    database = mongoClient['twitter-memories']
    return database.tweets


def initialize_users_db():
    mongoClient = MongoClient(CONFIG['MONGODB_ADDR'])
    database = mongoClient['twitter-memories']
    return database.users


def add_tweet_to_db(tweet_id, month, day):
    db = initialize_tweets_db()
    tweet = {
        'id' : tweet_id,
        'month': month,
        'day': day
    }
    db.insert_one(tweet)


def register_user(username, password, id):
    db = initialize_users_db()
    if is_username_used(username, db):
        return "Username is in use, pick another!"
    else:
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        # we have to decode the hash to we can store it as a string
        hashed = hashed.decode()
        user = {
            'id': id,
            'username': username,
            'password_hash': hashed
        }
        db.insert_one(user)
        return "Account registered successfully!"


def is_username_used(username, db):
    query = db.find({'username': username})
    if query.count() == 0:
        return False
    else:
        return True


def authenticated_user(username, password):
    db = initialize_users_db()
    user = db.find_one({ 'username': username})
    hashed = bcrypt.hashpw(password.encode(), user['password_hash'].encode())
    if user['password_hash'] == hashed.decode():
        return True
    else:
        return False
