from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from processingEngine.taskProcessor import process_csv_file
from databaseController.controllerDB import register_user, authenticated_user, fetch_user_by_id, fetch_user_by_username
from User import User
from config import CONFIG
import uuid, os

app = Flask(__name__)
app.secret_key = CONFIG['SECRET_KEY']
login_manager = LoginManager()
login_manager.init_app(app)
CORS(app)

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
def load_user(id):
    # should look for user in db and return the creation of a user object
    user_query = fetch_user_by_id(id)
    try:
        return User(user_query['id'], user_query['username'])
    except KeyError:
        return None


@app.route('/login', methods=['GET'])
def login():
    # First get args and authenticate user, Flask-Login part comes in next
    args = request.values
    usernm = args['username']
    passwd = args['password']
    if authenticated_user(usernm, passwd):
        # TODO: take advantage of reading from db in auth step and just create the User object from here
        user_query = fetch_user_by_username(usernm)
        user = User(user_query['id'], user_query['username'])
        login_user(user, remember=True)
        return jsonify({"status": "Login Successful!"})
    else:
        return jsonify({"status": "Wrong password!"})


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
    return jsonify({'status': response})


@app.route('/upload', methods=['POST'])
@login_required
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


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return "You are now logged out"


@app.route('/play', methods=['GET'])
@login_required
def play():
    print(current_user.username)
    return jsonify({"status": current_user.username})

if __name__ == '__main__':
    app.run(host=CONFIG['IP_ADDR'], port=5000)

# curl : curl -X POST --data "username=john" --data "password=lalala"  http://192.168.1.118:5000/register
# curl command : curl -X POST -F "file=@Downloads/2.csv" http://192.168.1.118:5000/upload
# to run celery worker celery -A processingEngine.taskProcessor worker --loglevel=info
# to run endpoint server python -m flaskWebServer.restEndpoints