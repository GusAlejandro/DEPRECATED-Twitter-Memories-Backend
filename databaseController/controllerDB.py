from pymongo import MongoClient
from config import CONFIG
"""
Defines set of functions to communicate with DB of choice. Used in /flaskWebServer and /processingEngine .

DATABASE SPECIFICATIONS
    * NoSQL DB (most likely MongoDB)
        * User has id, username, tweet archive file, collection of tweets
            * Collection of tweets broken down by months
"""


def initialize_db():
    mongoClient = MongoClient(CONFIG['MONGODB_ADDR'])
    database = mongoClient['twitter-memories']
    tweets = database.tweets
    return tweets


def add_tweet_to_db(tweet_id, month, day):
    db = initialize_db()
    tweet = {
        'id' : tweet_id,
        'month': month,
        'day': day
    }
    db.insert_one(tweet)


def register_user(username, password):
    pass

