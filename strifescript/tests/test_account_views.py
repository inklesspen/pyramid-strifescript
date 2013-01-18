import transaction

from nose import tools as nt

from pyramid import testing

from ..models import DBSession, User, NoResultFound
from .. import views, validation, models

from . import BaseTest
from . import fixtures as fix

from mock import MagicMock, patch, create_autospec

class TestRegistration(BaseTest):
    def test_successful(self):
        assert 0 == User.query.filter_by(username=u"test").count()

        request_body = {
            'username': u'test',
            'email': u'test@test.com',
            'password': u'test password'
        }

        header_key = 'Sample-Header'
        header_value = 'value'
        policy = self.config.testing_securitypolicy(userid=None, remember_result=[(header_key, header_value)])

        request = testing.DummyRequest(json_body=request_body, method='POST')
        actual = views.register(request)
        response = request.response
        user = User.query.filter_by(username=u"test").one()
        assert user.check_password(u"test password")

        assert header_value == response.headers[header_key]
        assert policy.remembered == user.id

        expected = {
            u'user': {
                u'username': request_body['username'],
                u'email': request_body['email']
            }
        }

        assert expected == actual

    def test_username_already_taken(self):
        self.add_fixtures(fix.users.UserData)

        request_body = {
            'username': fix.users.UserData.foo_user.username,
            'password': fix.users.UserData.foo_user._password
        }

        request = testing.DummyRequest(json_body=request_body, method='POST')
        actual = views.register(request)

        expected = {
            u'errors': {'username': [u"'foo' is already a registered username"]}
        }

        assert expected == actual

    def test_unsuccessful(self):
        assert 0 == User.query.count()

        request_body = {}

        request = testing.DummyRequest(json_body=request_body, method='POST')
        actual = views.register(request)
        assert 0 == User.query.count()

        expected = {
            u'errors': {'username': [u'Required'], 'password': [u'Required']}
        }

        assert expected == actual

class TestLogin(BaseTest):
    def test_login(self):
        timestamp = models.utcnow()
        self.add_patcher(patch.object(models, 'utcnow'))
        models.utcnow.return_value = timestamp

        self.add_fixtures(fix.users.UserData)

        request_body = {
            'username': fix.users.UserData.foo_user.username,
            'password': fix.users.UserData.foo_user._password
        }

        header_key = 'Sample-Header'
        header_value = 'value'
        policy = self.config.testing_securitypolicy(userid=None, remember_result=[(header_key, header_value)])

        request = testing.DummyRequest(json_body=request_body, method='POST')
        actual = views.login(request)
        user = User.query.filter_by(username=request_body['username']).one()
        expected = {u'current_user': user.username}
        assert expected == actual

        response = request.response
        assert header_value == response.headers[header_key]
        assert policy.remembered == user.id
        assert user.last_login == timestamp

    def test_bad_password(self):
        self.add_fixtures(fix.users.UserData)

        request_body = {
            'username': fix.users.UserData.foo_user.username,
            'password': fix.users.UserData.foo_user._password + "not it"
        }

        request = testing.DummyRequest(json_body=request_body, method='POST')
        actual = views.login(request)
        expected = {
            u'errors': validation.auth_errors()
        }
        assert expected == actual

        response = request.response
        assert 400 == response.code

    def test_bad_username(self):
        self.add_fixtures(fix.users.UserData)

        request_body = {
            'username': fix.users.UserData.foo_user.username + "nobody",
            'password': fix.users.UserData.foo_user._password
        }

        request = testing.DummyRequest(json_body=request_body, method='POST')
        actual = views.login(request)
        expected = {
            u'errors': validation.auth_errors()
        }
        assert expected == actual

        response = request.response
        assert 400 == response.code

class TestLogout(BaseTest):
    def test_logout(self):
        self.add_fixtures(fix.users.UserData)
        user = User.query.first()

        header_key = 'Sample-Header'
        header_value = 'value'
        policy = self.config.testing_securitypolicy(userid=user.id, forget_result=[(header_key, header_value)])

        request = testing.DummyRequest(method='POST')
        actual = views.logout(request)

        expected = {}
        assert expected == actual
        assert policy.forgotten
