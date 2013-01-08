from pyramid.security import Everyone, Authenticated, Allow, Deny, ALL_PERMISSIONS
from pyramid.httpexceptions import HTTPNotFound

from .models import User, NoResultFound

def get_principals(stored_id, request):
    try:
        login = Login.get_by_id(stored_id)
    except NoResultFound, e:
        return None
    principals = [login.id]
    return principals

