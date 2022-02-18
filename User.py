from DataBase import DATABASE

#Type constants
GOD = 0
ADMIN = 1
CLIENT = 2
DEFAULT = 3


class User:
    def __init__(self, data):
        self.id, self.alias, self.type = self._preprocess(data)

    @staticmethod
    def _preprocess(data):
        user_id, alias, user_type = data[0], data[1].strip(), data[2]
        return user_id, alias, user_type

    def is_god(self):
        return self.type == GOD


class Users:
    def __init__(self):
        self.users = list()
        self._set_users()

    def _set_users(self):
        users = list()
        data = DATABASE.select('telegram')
        for user in data:
            users.append(User(user))
        self.users = users

    def register(self, user_id, alias):
        assert len(alias) <= 15
        alias = alias.strip()
        if self.is_registered(user_id):
            return False
        DATABASE.insert("telegram", "id, alias", f"{user_id},'{alias}'")
        self._set_users()
        return True

    def get_i_ds(self):
        ids = [user.id for user in self.get_users()]
        return ids

    def get_users(self):
        return self.users

    def is_registered(self, user_id):
        if self.get_user(user_id) is None:
            return False
        return True

    def get_user(self, user_id):
        for user in self.users:
            if user.id == user_id:
                return user
        return None


USERS = Users()
