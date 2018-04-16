from flask import Flask, request, jsonify
from flask_login import LoginManager
from processingEngine.taskProcessor import process_csv_file
from databaseController.controllerDB import register_user, authenticated_user
from config import CONFIG
import uuid, os

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

"""
API ENDPOINTS:
    - /login [GET]
        * simply login to your account 
    - /register [POST]
        * register an account on the service 
    - /fileUpload [POST]
        * upload you tweet archive to your account
    - /dailyTweets [GET]
        * view the tweets you have made on this day from previous years
"""

@login_manager.user_loader
def load_user(username):
    # should look for user in db and return the creation of a user object
    return None

@app.route('/login', methods=['GET'])
def login():
    # First get args and authenticate user, Flask-Login part comes in next
    args = request.values
    usernm = args['username']
    passwd = args['password']
    if authenticated_user(usernm, passwd):
        # then we do flask-login session stuff
        return "Login successful!"
    else:
        return "Wrong password!"


@app.route('/register', methods=['POST'])
def register():
    """
    Adds new user to system. Needs username and password.
    """
    args = request.values
    usernm = args['username']
    passwd = args['password']
    id = str(uuid.uuid4())
    response = register_user(usernm, passwd, id)
    return jsonify(response)


@app.route('/upload', methods=['POST'])
def file_upload():
    """
    Add file to storage, add initial processing task to queue
    """
    csv_file = request.files['file']
    csv_file.filename = str(uuid.uuid4()) + ".csv"
    csv_file.save('FILES/' + csv_file.filename)
    data = {'file-code': csv_file.filename}
    process_csv_file.delay("FILES/" + csv_file.filename)
    return jsonify(data)


if __name__ == '__main__':
    app.run(host=CONFIG['IP_ADDR'], port=5000)

# curl : curl -X POST --data "username=john" --data "password=lalala"  http://192.168.1.118:5000/register
# curl command : curl -X POST -F "file=@Downloads/2.csv" http://192.168.1.118:5000/upload
# to run celery worker sys
# to run endpoint server python -m flaskWebServer.restEndpoints