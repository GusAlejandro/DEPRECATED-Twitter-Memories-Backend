from pymongo import MongoClient
from config import CONFIG
import bcrypt


"""
Defines set of functions to communicate with DB of choice. Used in /flaskWebServer and /processingEngine .

DATABASE SPECIFICATIONS
    * NoSQL DB (most likely MongoDB)
        * User has id, username, and password hash
        * Tweets has user id and array of tweets w/id, date, and month 
"""
# TODO: Refactor 'day' to 'date' in DB


def initialize_tweets_db():
    mongoClient = MongoClient(CONFIG['MONGODB_ADDR'])
    database = mongoClient['twitter-memories']
    return database.tweets


def initialize_users_db():
    mongoClient = MongoClient(CONFIG['MONGODB_ADDR'])
    database = mongoClient['twitter-memories']
    return database.users


def add_tweet_to_db(user_id, tweet_id, month, day):
    db = initialize_tweets_db()
    tweet = {
        'id' : tweet_id,
        'month': month,
        'day': day
    }
    db.find_one_and_update(
        {'user_id': user_id},
        {'$addToSet': {'tweets': tweet}}
    )


def register_user(username, password, id):
    tweets = initialize_tweets_db()
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
            'password_hash': hashed,
            'file_uploaded': False
        }
        db.insert_one(user)
        tweet_collection = {
            'user_id': id,
            'tweets': []
        }
        tweets.insert_one(tweet_collection)
        return "Account registered successfully! You can now login !"


def is_username_used(username, db):
    query = db.find({'username': username})
    if query.count() == 0:
        return False
    else:
        return True


def check_password(username, password):
    """
    Takes username and password and verifies them, returns bool and fetched user
    """
    db = initialize_users_db()
    user = db.find_one({ 'username': username})
    try:
        hashed = bcrypt.hashpw(password.encode(), user['password_hash'].encode())
        if user['password_hash'] == hashed.decode():
            return True, user
        else:
            return False, user
    except TypeError:
        return False, user


def get_tweets(user_id, month, date):
    # format of month/date: MM & DD
    db = initialize_tweets_db()
    # Aggregate query that checks for a specific user_id, then looks for a matching month and day tweets
    query = db.aggregate([
    {
        '$match': {
            'user_id': user_id
        }
    }, {
        '$unwind': '$tweets'
    }, {
        '$match': {
            '$and': [ {'tweets.month': month}, {'tweets.day':date}]
        }
    }
    ])
    tweets = []
    for data in query:
        tweets.append(data['tweets'])
    if tweets:
        return tweets
    else:
        return "No tweets found"


def get_user_by_id(user_id):
    db = initialize_users_db()
    user = db.find_one({'id': user_id})
    return user


def mark_file_upload(user_id):
    db = initialize_users_db()
    db.updae({'id': user_id}, {'file_uploaded': True})