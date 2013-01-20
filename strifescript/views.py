from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response
from pyramid.view import view_config
from pyramid import security

import transaction

from .models import (
    DBSession,
    User,
    Team,
    Conflict,
    SetScriptEvent,
    NoResultFound
    )

from . import validation, censoring

@view_config(route_name='home', renderer='mytemplate.mako')
def home(request):
    return {'project': 'strifescript'}

@view_config(route_name='register', renderer='json')
def register(request):
    try:
        validated = validation.Registration().deserialize(request.json_body)
    except validation.Invalid, e:
        transaction.doom()
        return {u'errors': validation.collect_errors(e)}

    new_user = User.new(**validated)
    DBSession.add(new_user)
    DBSession.flush()
    headers = security.remember(request, new_user.id)
    request.response.headers = headers
    return {'user': new_user.for_json()}

@view_config(route_name='login', renderer='json')
def login(request):
    try:
        validated = validation.PlausibleLogin().deserialize(request.json_body)
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

    user.update_last_login()
    headers = security.remember(request, user.id)
    request.response.headers = headers
    return {u'current_user': user.username}

@view_config(route_name='logout', renderer='json')
def logout(request):
    headers = security.forget(request)
    request.response.headers = headers
    return {}

@view_config(route_name='conflict', request_method='POST', renderer='json')
def create_conflict(request):
    try:
        validated = validation.Conflict().bind(current_user=request.current_user).deserialize(request.json_body)
    except validation.Invalid, e:
        request.response = HTTPBadRequest()
        return {u'errors': validation.collect_errors(e)}

    conflict = Conflict.from_validated(validated)
    DBSession.add(conflict)
    DBSession.flush()

    return {'id': conflict.id}

@view_config(route_name='conflict_id', request_method='GET', renderer='json')
def conflict_info(request):
    conflict = request.context.conflict
    # TODO: censoring needs to be a separate step
    # FYI: the fact that a team can change actions (because it has enough actions to change) is priviliged information and must be censored
    info = conflict.for_json()
    info['action_choices'] = censoring.censor_allowed_actions(info['action_choices'], request.current_user)
    info['exchanges'] = censoring.censor_conflict_history(info['exchanges'], request.current_user)
    return info

@view_config(route_name='conflict.action', request_method='POST', renderer='json')
def conflict_action(request):
    conflict = request.context.conflict
    try:
        validated = validation.TeamAuthorization().bind(current_user=request.current_user, current_conflict=request.context.conflict).deserialize(request.json_body)
    except validation.Invalid, e:
        request.response = HTTPBadRequest()
        return {u'errors': validation.collect_errors(e)}

    team = validated['team']
    allowed_actions = conflict.allowed_actions()[team]
    if validated['action'] not in allowed_actions:
        request.response = HTTPBadRequest()
        return {u'errors': validation.simple_errors(dict(action=u"That action is not allowed for that team"))}

    if validated['action'] == 'set-script':
        try:
            validated = validation.SetScriptEvent().deserialize(request.json_body)
        except validation.Invalid, e:
            request.response = HTTPBadRequest()
            return {u'errors': validation.collect_errors(e)}
        validated['team'] = team
        validated['exchange'] = conflict.current_exchange()
        event = SetScriptEvent.from_validated(validated)
    else:
        raise NotImplementedError()

    event.user = request.current_user
    event.conflict = conflict
    DBSession.add(event)
    return {}

def archive_conflict(request):
    conflict = request.context.conflict
    if conflict.archived:
        request.response = HTTPBadRequest()
        return {u'errors': validation.simple_errors(archived=u"Already archived.")}
    conflict.archived = True
    return {}
