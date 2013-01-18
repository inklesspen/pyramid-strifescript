from nose import tools as nt

from pyramid import testing

from ..models import DBSession, User, Conflict, Team, NoResultFound
from .. import views, validation, models, acl

from . import BaseTest
from . import fixtures as fix

from mock import MagicMock, patch, create_autospec

class TestCreateConflict(BaseTest):
    def test_successful_create(self):
        self.add_fixtures(fix.users.UserData)

        alice = User.query.filter_by(username=fix.users.UserData.alice.username).one()

        request_body = {
            'name': "The Glorious Battle",
            'teams': [
                {
                    'name': 'Team A',
                    'participants': [fix.users.UserData.alice.username, fix.users.UserData.bob.username],
                    'notes': "Alice and Bob's team",
                },
                {
                    'name': 'Team 1',
                    'participants': [fix.users.UserData.claire.username, fix.users.UserData.danny.username],
                    'notes': "The other guys",
                },
            ]
        }

        request = testing.DummyRequest(json_body=request_body, method='POST', current_user=alice)
        actual = views.create_conflict(request)

        conflict = Conflict.query.one()
        assert conflict.name == request_body['name']

        expected = {'id': conflict.id}
        assert expected == actual

class TestConflictInfo(BaseTest):
    def test_get_info(self):
        self.add_fixtures(fix.bare_conflict.ConflictData)

        alice = User.query.filter_by(username=fix.users.UserData.alice.username).one()

        conflict = Conflict.query.get(fix.bare_conflict.ConflictData.conflict.id)

        npc_team = Team.query.filter_by(conflict=conflict, name=u"NPC Team").one()
        pc_team = Team.query.filter_by(conflict=conflict, name=u"PC Team").one()

        request = testing.DummyRequest(method='GET', current_user=alice, matchdict=dict(id=conflict.id))
        request.context = acl.Conflict(request)
        actual = views.conflict_info(request)
        expected = {
            'id': fix.bare_conflict.ConflictData.conflict.id,
            'name': fix.bare_conflict.ConflictData.conflict.name,
            'teams': [
                {
                    'id': npc_team.id,
                    'name':npc_team.name,
                    'notes': npc_team.notes,
                    'participants': [fix.users.UserData.alice.username],
                },
                {
                    'id': pc_team.id,
                    'name': pc_team.name,
                    'participants': [
                        fix.users.UserData.bob.username,
                        fix.users.UserData.claire.username,
                        fix.users.UserData.danny.username
                    ],
                }
            ],
            'action_choices': {
                npc_team.id: ['set-script'],
                pc_team.id: ['set-script'],
            }
        }
        assert expected == actual

class TestArchiveConflict(BaseTest):
    def test_archive(self):
        self.add_fixtures(fix.bare_conflict.ConflictData)

        alice = User.query.filter_by(username=fix.users.UserData.alice.username).one()

        conflict = Conflict.query.get(fix.bare_conflict.ConflictData.conflict.id)
        assert not conflict.archived

        request_body = {
        }

        request = testing.DummyRequest(json_body=request_body, method='POST', current_user=alice, matchdict=dict(id=conflict.id))
        request.context = acl.Conflict(request)
        actual = views.archive_conflict(request)

        conflict = Conflict.query.get(fix.bare_conflict.ConflictData.conflict.id)
        assert conflict.archived

    def test_already_archived(self):
        self.add_fixtures(fix.archived_conflict.ConflictData)

        alice = User.query.filter_by(username=fix.users.UserData.alice.username).one()
        conflict = Conflict.query.get(fix.archived_conflict.ConflictData.conflict.id)
        assert conflict.archived

        request_body = {
        }

        request = testing.DummyRequest(json_body=request_body, method='POST', current_user=alice, matchdict=dict(id=conflict.id))
        request.context = acl.Conflict(request)
        actual = views.archive_conflict(request)
        expected = {
            u'errors': {
                'archived': [u'Already archived.']
            }
        }

        response = request.response
        assert 400 == response.code

