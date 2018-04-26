class User:

    def __init__(self, id, username):
        self.id = id
        self.username = username

    def get_username(self):
        return self.username

    def get_id(self):
        return self.id
