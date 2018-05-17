from databaseController import controllerDB
from bs4 import BeautifulSoup
import csv, time, requests
from celery import Celery
from config import CONFIG, auth_login, WORKER_CONFIG, FB_CONFIG
import requests
import pyrebase


"""
Fetches tasks from the job queue and executes them.
Requires access to DB via controller, same as the one used in web server.


TASKS
    * Processing tweet archive file from CSV file to DB format
        * Tweet Object
            - id
            - date



"""
app = Celery(broker=CONFIG['MESSAGE_BROKER'])
app.config_from_object('celeryconfig')
firebase = pyrebase.initialize_app(FB_CONFIG)
fb_auth = firebase.auth()


def get_date_for_tweet(id):
    """
    EARLY PERFORMANCE EVALUATIONS SHOW THIS TAKES TOO LONG TO DO FOR ALL TWEETS AT INITIAL SUBMISSION (40min+), NOT USING FOR NOW  ¯\_(ツ)_/¯

    Since we are checking the date for all tweets, might as well just use this as a get date function
    data: [day, month, year]
    """
    req = requests.get("https://twitter.com/user/status/" + str(id))
    raw_html = req.text
    soup = BeautifulSoup(raw_html, 'html.parser')
    tag = soup.find("div",{"class":"client-and-actions"})
    try:
        tag = tag.contents
        raw_data = tag[1].find("span").getText()
        curr = ""
        data = []
        for item in raw_data:
            if item == " ":
                data.append(curr)
                curr = ""
            else:
                curr = curr + item
        data.append(curr)
        del data[0]
        del data[0]
        del data[0]
        print(data)
        return data
    except AttributeError:
        print("page was suspended or private or other error ")


@app.task()
def process_csv_file(file_name, user_id):
    """
    Main function to process single csv file into database entries
    """
    # First step is to download the file from the web server
    auth_login['file'] = file_name
    r = requests.get(WORKER_CONFIG['FILE_DOWNLOAD_ENDPOINT'], auth_login)
    open('processingEngine/' + file_name, 'wb').write(r.content)
    # print("PROCESS HAS FINISHED")
    db_tweets = controllerDB.initialize_tweets_db()
    db_users = controllerDB.initialize_users_db()
    with open('processingEngine/'+file_name, newline='') as csvfile:
        tweet_reader = csv.reader(csvfile, delimiter=',')
        next(tweet_reader)
        for row in tweet_reader:
            tweet_id = row[0]
            std_date = row[3][:10]
            month = std_date[5:7]
            day = std_date[8:10]
            if int(month) >= 5:
                controllerDB.add_tweet_to_db(db_tweets, user_id,tweet_id, month, day)
                print("tweet: " + tweet_id + " is now done")
                print("the day was: " + day)
                #         print("the month was: " + month)
    controllerDB.set_file_status(db_users, user_id, '2')

