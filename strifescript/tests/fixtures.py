from ..models import User

from fixture import DataSet

class UserData(DataSet):
    class foo_user:
        username = u"foo"
        email = u"foo@example.com"
        _password = "foofoofoo"
        password_hash = User.generate_password_hash(_password, difficulty=2)
