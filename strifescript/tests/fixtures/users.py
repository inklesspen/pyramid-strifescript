from ...models import User

from fixture import DataSet

class UserData(DataSet):
    class foo_user:
        username = u"foo"
        email = u"foo@example.com"
        _password = "foofoofoo"
        password_hash = User.generate_password_hash(_password, difficulty=2)
    class alice:
        username = u"alice"
        email = u"alice@example.com"
        _password = "alice's password"
        password_hash = User.generate_password_hash(_password, difficulty=2)
    class bob:
        username = u"bob"
        email = u"bob@example.com"
        _password = "bob's password"
        password_hash = User.generate_password_hash(_password, difficulty=2)
    class claire:
        username = u"claire"
        email = u"claire@example.com"
        _password = "claire's password"
        password_hash = User.generate_password_hash(_password, difficulty=2)
    class danny:
        username = u"danny"
        email = u"danny@example.com"
        _password = "danny's password"
        password_hash = User.generate_password_hash(_password, difficulty=2)
