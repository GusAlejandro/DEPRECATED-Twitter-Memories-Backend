from flask import Flask, request, jsonify, g, send_from_directory
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from processingEngine.taskProcessor import process_csv_file
from databaseController.controllerDB import register_user, check_password, get_tweets, set_file_status, get_file_status, initialize_users_db
from User import User
from config import CONFIG, auth_login
import uuid
import os


app = Flask(__name__)
auth = HTTPBasicAuth()
CORS(app)


def authenticate_request_for_file(email, password):
    # TODO: everything is done via plaintext, ideally we want this to be stored as a hash
    # TODO: Look into just using 3rd party auth service
    if email == auth_login['email'] and password == auth_login['password']:
        return True
    else:
        return False


@auth.verify_password
def verify_pw(username_or_token, password):
    """
    used by login_required decorator to authenticate requests via username/password combo or token
    """
    user = User.verify_token(username_or_token)
    if not user:
        is_auth, user = check_password(username_or_token, password)
        if not user or not is_auth:
            return False
        g.user = User(user['id'], user['username'])
        return True
    g.user = user
    return True


"""
Below are the API endpoints that the client will use
"""

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
def check_file_status():
    """
    Used by web app to check status on processing Twitter Archive file.
    """
    return jsonify({'file_status': get_file_status(g.user.get_id())})


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
    data = {'file-code': csv_file.filename}
    process_csv_file.delay(csv_file.filename, g.user.get_id())
    db = initialize_users_db()
    set_file_status(db, g.user.get_id(), '1')
    return jsonify(data)


@app.route('/api/tweets', methods=['GET'])
@auth.login_required
def get_daily_tweets():
    """
    Takes month and date in format MM and DD, respectively, returns user tweets for that day.
    """
    args = request.values
    month = args['month']
    date = args['date']
    # format of month/date: MM & DD
    response = get_tweets(g.user.get_id(), month, date)
    return jsonify({'TWEETS': response})


"""
Below are the endpoints that the celery worker process will use, seperate from the client endpoints 
"""


@app.route('/api/download', methods=['GET'])
def file_download():
    args = request.values
    email = args['email']
    password = args['password']
    if authenticate_request_for_file(email, password):
        file_name = args['file']
        path = os.path.abspath('FILES')
        return send_from_directory(directory=path, filename=file_name)
    else:
        return jsonify({'request-status': 'ACCESS DENIED'})


# if __name__ == '__main__':
#     app.run(host=CONFIG['IP_ADDR'], threaded=True ,port=5000)

# curl : curl -X POST --data "username=john" --data "password=lalala"  http://192.168.1.118:5000/register
# curl command : curl -X POST -F "file=@Downloads/2.csv" http://192.168.1.118:5000/upload
# to run celery worker celery -A processingEngine.taskProcessor worker --loglevel=info
# to run endpoint server python -m flaskWebServer.restEndpoints