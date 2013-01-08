import unittest
import transaction

from nose import tools as nt

from pyramid import testing

from ..models import DBSession, User, NoResultFound, PasswordLogin
from .. import views

from . import BaseTest

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
        assert policy.remembered == user.login.id

        expected = {
            u'user': {
                u'username': request_body['username'],
                u'email': request_body['email']
            }
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
