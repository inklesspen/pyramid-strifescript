import colander

from colander import (
    Sequence,
    MappingSchema,
    SequenceSchema,
    SchemaNode,
    String,
    Boolean,
    Date,
    Integer,
    All,
    Length,
    Range,
    Email,
    Invalid,
    Function,
    OneOf
)

from . import models

from webob.multidict import MultiDict

def username_can_be_registered(node, value):
    if models.User.user_exists_with_username(value):
        raise Invalid(node, u"'%s' is already a registered username" % value)
    return None

class Registration(MappingSchema):
    username = SchemaNode(String(), validator=All(Length(max=50), username_can_be_registered))
    email = SchemaNode(String(), validator=All(Email(), Length(min=3, max=254)), missing=None)
    password = SchemaNode(String(), validator=Length(min=5))

class PlausibleLogin(MappingSchema):
    username = SchemaNode(String(), validator=Length(max=50))
    password = SchemaNode(String(), validator=Length(min=5))

@colander.deferred
def deferred_team_validation(node, kw):
    user = kw.get('current_user')
    if user is None:
        raise Exception('must bind current_user')

    def validator(node, value):
        for team in value:
            if user in team['participants']:
                return None
        raise colander.Invalid(node, "Current user must be on at least one team")
    return colander.All(validator, colander.Length(2))

class UserByUsername(object):
    def serialize(self, node, appstruct):
        if appstruct is colander.null:
            return colander.null
        if not isinstance(appstruct, models.User):
            raise colander.Invalid(node, "%r is not a User" % appstruct)
        return appstruct.username

    def deserialize(self, node, cstruct):
        if cstruct is colander.null:
            return colander.null
        if not isinstance(cstruct, basestring):
            raise colander.Invalid(node, "%r is not a string" % cstruct)
        try:
            value = models.User.query.filter_by(username=cstruct).one()
        except models.NoResultFound, e:
            raise colander.Invalid(node, "%r is not a valid username" % cstruct)
        return value

class Team(colander.MappingSchema):
    name = colander.SchemaNode(colander.String(), validator=colander.Length(1))
    participants = colander.SchemaNode(colander.Sequence(), colander.SchemaNode(UserByUsername()), validator=colander.Length(1))
    notes = colander.SchemaNode(colander.String(), missing=None)

class Conflict(MappingSchema):
    name = colander.SchemaNode(colander.String(), validator=colander.Length(1))
    teams = colander.SchemaNode(colander.Sequence(), Team(), validator=deferred_team_validation)

def can_act_for_team_validation(user):
    def validator(node, value):
        if user in value.users:
            return None
        raise colander.Invalid(node, "Current user must be on the specified team")
    return validator

def team_is_in_conflict_validation(conflict):
    def validator(node, value):
        if conflict is value.conflict:
            return None
        raise colander.Invalid(node, "The specified team must be in the current conflict")
    return validator

@colander.deferred
def deferred_check_team(node, kw):
    user = kw.get('current_user')
    if user is None:
        raise Exception('must bind current_user')
    conflict = kw.get('current_conflict')
    if conflict is None:
        raise Exception('must bind current_conflict')
    return colander.All(can_act_for_team_validation(user), team_is_in_conflict_validation(conflict))

class TeamById(object):
    def serialize(self, node, appstruct):
        raise NotImplementedError()
    def deserialize(self, node, cstruct):
        if cstruct is colander.null:
            return colander.null
        if not isinstance(cstruct, int):
            raise colander.Invalid(node, "%r is not an integer" % cstruct)
        try:
            value = models.Team.query.filter_by(id=cstruct).one()
        except models.NoResultFound, e:
            raise colander.Invalid(node, "%r is not a valid team id" % cstruct)
        return value

class TeamAuthorization(MappingSchema):
    action = colander.SchemaNode(colander.String(), validator=colander.OneOf(['set-script', 'reveal-volley', 'change-actions']))
    team = colander.SchemaNode(TeamById(), validator=deferred_check_team)

class SetScriptEvent(MappingSchema):
    script = colander.SchemaNode(colander.Sequence(), colander.SchemaNode(colander.Sequence(), colander.SchemaNode(colander.String()), validator=colander.Length(min=1)), validator=colander.Length(min=3, max=3))

@colander.deferred
def deferred_check_volley(node, kw):
    script = kw.get('script')
    if script is None:
        raise Exception('must bind script')
    def validator(node, value):
        if len(script[value - 1]) > 2:
            raise Invalid(node, "The specified volley does not have enough actions to change an action.")
        return None
    return All(Range(min=1, max=3), validator)

class ChangeActionsVolleyCheck(MappingSchema):
    volley_no = SchemaNode(Integer(), validator=deferred_check_volley)

@colander.deferred
def deferred_check_action_present(node, kw):
    volley = kw.get('volley')
    if volley is None:
        raise Exception('must bind volley')
    def validator(node, value):
        if value not in volley:
            raise Invalid(node, "The specified volley does not contain the action %r" % value)
        return None
    return validator

class ChangeActionsEvent(MappingSchema):
    forfeited_action = SchemaNode(String(), validator=deferred_check_action_present)
    changed_action = SchemaNode(String(), validator=deferred_check_action_present)
    replacement_action = SchemaNode(String(), validator=Length(min=1))

def _add_messages(md, key, error_node):
    for msg in error_node.messages():
        if hasattr(msg, 'interpolate'):
            msg = msg.interpolate()
        md.add(key, msg)

def collect_errors(error_exc):
    collected = MultiDict()
    # Any root-level errors?
    _add_messages(collected, '__form__', error_exc)
    for child in error_exc.children:
        key = child.node.name
        _add_messages(collected, key, child)
    return collected.dict_of_lists()

def auth_errors():
    collected = MultiDict()
    collected.add('username', u'Invalid username or password.')
    collected.add('password', u'Invalid username or password.')
    return collected.dict_of_lists()

def simple_errors(**kwargs):
    collected = MultiDict(kwargs)
    return collected.dict_of_lists()
