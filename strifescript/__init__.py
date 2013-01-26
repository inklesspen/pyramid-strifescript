from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )

from .acl import get_principals, get_user

def add_routes(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('register', '/api/register')
    config.add_route('login', '/api/login')
    config.add_route('logout', '/api/logout')
    config.add_route('conflict', '/api/conflict', factory='strifescript.acl.Conflict')
    config.add_route('conflicts', '/api/conflicts', factory='strifescript.acl.Conflict')
    config.add_route('conflict_id', '/api/conflict/{id}', factory='strifescript.acl.Conflict')
    config.add_route('conflict.action', '/api/conflict/{id}/action', factory='strifescript.acl.Conflict')

def add_request_methods(config):
    config.add_request_method(get_user, 'current_user', property=True, reify=True)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    auth_tkt_secret = settings['auth_tkt.secret']

    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    authn_policy = AuthTktAuthenticationPolicy(auth_tkt_secret, get_principals, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(settings=settings)
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.include(add_request_methods)
    config.include(add_routes)

    config.scan()
    return config.make_wsgi_app()
