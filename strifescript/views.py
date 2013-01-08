from pyramid.response import Response
from pyramid.view import view_config
from pyramid import security

import transaction
from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    User,
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
