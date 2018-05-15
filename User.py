from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from config import CONFIG
from databaseController.controllerDB import get_user_by_id


class User:

    def __init__(self, id, username):
        self.id = id
        self.username = username

    def get_username(self):
        return self.username

    def get_id(self):
        return self.id

    def generate_token(self, expiration=600):
        s = Serializer(CONFIG['SECRET_KEY'], expires_in=expiration);
        return s.dumps({'user_id': self.get_id()})

    @staticmethod
    def verify_token(token):
        s = Serializer(CONFIG['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        query = get_user_by_id(data['user_id'])
        user = User(query['id'],query['username'])
        return user
