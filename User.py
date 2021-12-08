from DataBase import DATABASE
from werkzeug.security import generate_password_hash, check_password_hash


#Type constants
GOD = 0
ADMIN = 1
CLIENT = 2
DEFAULT = 3


class User:
    def __init__(self,data):
        self.id, self.name, self.password, self.type, self.phone = self._preprocess(data)

    def _preprocess(self, data):
        id, name, password, type, phone = data[0], data[1].strip(), data[2].strip(), data[3], data[4]
        return id, name, password, type, phone


class Users:
    def __init__(self):
        self.users = list()
        self._set_users()


    def _set_users(self):
        users = list()
        data = DATABASE.select('users')
        for user in data:
            users.append(User(user))
        self.users = users

    def register(self, name, phone, password):
        for user in self.users:
            if user.name == name or user.phone == phone:
                return False

        password = generate_password_hash(password)
        DATABASE.insert("users", "username,phone,password,type", f"'{name}',{phone},'{password}',{DEFAULT}")
        self._set_users()
        return True

    def login(self, name, password):
        for user in self.users:
            if name == user.name:
                if check_password_hash(user.password, password):
                    return True
        return False


USERS = Users()