from ..models import PasswordLogin

from fixture import DataSet
class PasswordLoginData(DataSet):
    class foo_password:
        _password = "foofoofoo"
        password_hash = PasswordLogin.generate_password_hash(_password, difficulty=2)

class UserData(DataSet):
    class foo_user:
        username = u"foo"
        email = u"foo@example.com"
        logins = [PasswordLoginData.foo_password]
