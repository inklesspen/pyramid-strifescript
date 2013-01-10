from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response
from pyramid.view import view_config
from pyramid import security

import transaction

from .models import (
    DBSession,
    User,
    NoResultFound
    )

from . import validation

@view_config(route_name='home', renderer='mytemplate.mako')
def home(request):
    return {'project': 'strifescript'}

def register(request):
    try:
        validated = validation.Registration().deserialize(request.json_body)
    except validation.Invalid, e:
        transaction.doom()
        return {u'errors': validation.collect_errors(e)}

    new_user = User.new(**validated)
    DBSession.add(new_user)
    DBSession.flush()
    headers = security.remember(request, new_user.login.id)
    request.response.headers = headers
    return {'user': new_user.for_json()}

def login(request):
    try:
        validated = validation.PlausiblePasswordLogin().deserialize(request.json_body)
    except validation.Invalid, e:
        request.response = HTTPBadRequest()
        return {u'errors': validation.collect_errors(e)}
    try:
        user = User.query.filter_by(username=validated['username']).one()
    except NoResultFound, e:
        request.response = HTTPBadRequest()
        return {u'errors': validation.auth_errors()}

    if not user.check_password(validated['password']):
        request.response = HTTPBadRequest()
        return {u'errors': validation.auth_errors()}

    headers = security.remember(request, user.login.id)
    request.response.headers = headers
    return {u'current_user': user.username}

def logout(request):
    headers = security.forget(request)
    request.response.headers = headers
    return {}
