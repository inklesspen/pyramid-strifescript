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
    Email,
    Invalid,
    Function,
    OneOf
)

from . import models

from webob.multidict import MultiDict

class Registration(MappingSchema):
    username = SchemaNode(String(), validator=Length(max=50))
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
