from databaseController import controllerDB
from bs4 import BeautifulSoup
import csv, time, requests
from celery import Celery
from config import CONFIG
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
def process_csv_file(filepath, user_id):
    """
    Main function to process single csv file into database entries
    """
    with open(filepath, newline='') as csvfile:
        tweet_reader = csv.reader(csvfile, delimiter=',')
        skipTop = False
        for row in tweet_reader:
            if skipTop:
                tweet_id = row[0]
                std_date = row[3][:10]
                month = std_date[5:7]
                day = std_date[8:10]
                # TODO: Currently has to open a connection to db on each tweet addition, maybe push all at once ? Store in local redis and then bulk upload ???
                controllerDB.add_tweet_to_db(user_id,tweet_id, month, day)
                print("tweet: " + tweet_id + " is now done")
                print("the day was: " + day)
                print("the month was: " + month)
            else:
                skipTop = True
