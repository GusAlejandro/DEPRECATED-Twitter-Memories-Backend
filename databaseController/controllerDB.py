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


def add_tweet_to_db(user_id, tweet_id, month, day):
    # TODO: will just use the update instead of inser_one
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
            'password_hash': hashed
        }
        db.insert_one(user)
        tweet_collection = {
            'user_id': id,
            'tweets': []
        }
        tweets.insert_one(tweet_collection)
        return "Account registered successfully!"


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
    print("Running the quuery for user_id: " + user_id, "for the month: " + month, "for the day: " + date)
    # format of month/date: MM & DD
    db = initialize_tweets_db()
    # TODO: figure this query out, only returning the first tweet found, not all
    # x = db.find({ "user_id": user_id}, {'tweets': { '$elemMatch' : { 'month': month, 'day':date} } })
    #x = db.find({"user_id": user_id}, {'tweets': {'$elemMatch': {'month': month, 'day': date}}})
    x = db.find({'tweets.day': date})
    print("HERE: " + str(x.count()))
    for tweets in x:
        print(tweets)
    return None


# def fetch_user_by_id(id):
#     db = initialize_users_db()
#     user = db.find_one({'id': id})
#     return user
#
#
# def fetch_user_by_username(username):
#     db = initialize_users_db()
#     user = db.find_one({'username': username})
#     return user
