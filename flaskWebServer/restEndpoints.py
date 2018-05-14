from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from processingEngine.taskProcessor import process_csv_file
from databaseController.controllerDB import register_user, check_password, get_tweets, set_file_status, upload_file
from User import User
from config import CONFIG, FB_CONFIG, auth_login
import uuid
import pyrebase

app = Flask(__name__)
auth = HTTPBasicAuth()
CORS(app)
firebase = pyrebase.initialize_app(FB_CONFIG)
fb_auth = firebase.auth()


"""
API ENDPOINTS:
    - /register [POST]
        * register an account on the service 
    - /fileUpload [POST]
        * upload you tweet archive to your account
    - /tweets [GET]
        * view the tweets you have made on this day from previous years
    - /token [GET]
        * Sets the user token, acting like a login route 
"""


@auth.verify_password
def verify_pw(username_or_token, password):
    user = User.verify_token(username_or_token)
    if not user:
        is_auth, user = check_password(username_or_token, password)
        if not user or not is_auth:
            return False
        g.user = User(user['id'], user['username'], user['file_uploaded'])
        return True
    g.user = user
    return True


@app.route('/api/token', methods=['GET'])
@auth.login_required
def get_auth_token():
    token = g.user.generate_token()
    return jsonify({'token': token.decode('ascii')})


@app.route('/api/register', methods=['POST'])
def register():
    """
    Adds new user to system. Needs username and password.
    """
    args = request.get_json()
    usernm = args['username']
    passwd = args['password']
    id = str(uuid.uuid4())
    response = register_user(usernm, passwd, id)
    return jsonify({'status': response})


@app.route('/api/file_status', methods=['GET'])
@auth.login_required
def get_file_status():
    return jsonify({'file_status': g.user.get_file_status()})


# TODO: Works, but takes a bit too long. Might want to make it async or offload upload to another server
@app.route('/api/upload', methods=['POST'])
@auth.login_required
def file_upload():
    """
    Add file to storage, add initial processing task to queue
    """
    csv_file = request.files['file']
    csv_file.filename = str(uuid.uuid4()) + ".csv"
    csv_file.save('FILES/' + csv_file.filename)
    upload_file(firebase, csv_file.filename, 'FILES/' + csv_file.filename, fb_auth)
    data = {'file-code': csv_file.filename}
    # process_csv_file.delay("FILES/" + csv_file.filename, g.user.get_id())
    set_file_status(g.user.get_id(), '1')
    return jsonify(data)


@app.route('/api/tweets', methods=['GET'])
@auth.login_required
def get_daily_tweets():
    args = request.values
    month = args['month']
    date = args['date']
    # format of month/date: MM & DD
    response = get_tweets(g.user.get_id(), month, date)
    return jsonify({'TWEETS': response})

if __name__ == '__main__':
    app.run(host=CONFIG['IP_ADDR'], port=5000)

# curl : curl -X POST --data "username=john" --data "password=lalala"  http://192.168.1.118:5000/register
# curl command : curl -X POST -F "file=@Downloads/2.csv" http://192.168.1.118:5000/upload
# to run celery worker celery -A processingEngine.taskProcessor worker --loglevel=info
# to run endpoint server python -m flaskWebServer.restEndpoints