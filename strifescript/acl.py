from pyramid.security import Everyone, Authenticated, Allow, Deny, ALL_PERMISSIONS, authenticated_userid
from pyramid.httpexceptions import HTTPNotFound

from . import models

def get_principals(stored_id, request):
    try:
        login = models.User.query.filter_by(id=stored_id).one()
    except models.NoResultFound, e:
        return None
    principals = [login.id]
    return principals

def get_user(request):
    user_id = authenticated_userid(request)
    if user_id is None:
        return None
    return models.User.query.get(user_id)

class Base(object):
    __acl__ = [(Allow, Authenticated, 'view')]
    def __init__(self, request):
        """This __init__ is required so that the instantiation can happen."""
        pass

    def __repr__(self):
        return u"<ACL type {0} with settings {1!r}>".format(type(self), self.__acl__)

class Conflict(Base):
    def __init__(self, request):
        if 'id' in request.matchdict:
            try:
                conflict = models.Conflict.query.filter_by(id=request.matchdict['id']).one()
            except models.NoResultFound, e:
                raise HTTPNotFound()

            self.conflict = conflict
            self.__acl__ = [(Allow, user.id, ALL_PERMISSIONS) for user in conflict.users]
        else:
            self.__acl__ = [(Allow, Authenticated, 'create')]
