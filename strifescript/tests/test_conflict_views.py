import unittest

from nose import tools as nt

from pyramid import testing

from ..models import DBSession, User, Conflict, NoResultFound
from .. import views, validation, models, acl

from . import BaseTest
from . import fixtures as fix

from mock import MagicMock, patch, create_autospec

class TestCreateConflict(BaseTest):
    def test_successful_create(self):
        self.add_fixtures(fix.UserData)

        alice = User.query.filter_by(username=fix.UserData.alice.username).one()

        request_body = {
            'name': "The Glorious Battle",
            'teams': [
                {
                    'name': 'Team A',
                    'participants': [fix.UserData.alice.username, fix.UserData.bob.username],
                    'notes': "Alice and Bob's team",
                },
                {
                    'name': 'Team 1',
                    'participants': [fix.UserData.claire.username, fix.UserData.danny.username],
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
        self.add_fixtures(fix.ConflictData)

        alice = User.query.filter_by(username=fix.UserData.alice.username).one()
        conflict = Conflict.query.get(fix.ConflictData.conflict.id)

        request = testing.DummyRequest(method='GET', current_user=alice, matchdict=dict(id=conflict.id))
        request.context = acl.Conflict(request)
        actual = views.conflict_info(request)
        expected = {
            'id': fix.ConflictData.conflict.id,
            'name': fix.ConflictData.conflict.name,
            'teams': [
                {
                    'id': fix.TeamData.npc_team.id,
                    'name': fix.TeamData.npc_team.name,
                    'notes': fix.TeamData.npc_team.notes,
                    'participants': [fix.UserData.alice.username],
                },
                {
                    'id': fix.TeamData.pc_team.id,
                    'name': fix.TeamData.pc_team.name,
                    'participants': [
                        fix.UserData.bob.username,
                        fix.UserData.claire.username,
                        fix.UserData.danny.username
                    ],
                }
            ],
            'actions': {
                fix.TeamData.npc_team.id: ['set-script'],
                fix.TeamData.pc_team.id: ['set-script'],
            }
        }
        assert expected == actual

class TestArchiveConflict(BaseTest):
    def test_archive(self):
        self.add_fixtures(fix.ConflictData)

        alice = User.query.filter_by(username=fix.UserData.alice.username).one()
        conflict = Conflict.query.get(fix.ConflictData.conflict.id)
        assert not conflict.archived

        request_body = {
        }

        request = testing.DummyRequest(json_body=request_body, method='POST', current_user=alice, matchdict=dict(id=conflict.id))
        request.context = acl.Conflict(request)
        actual = views.archive_conflict(request)

        conflict = Conflict.query.get(fix.ConflictData.conflict.id)
        assert conflict.archived

    def test_already_archived(self):
        self.add_fixtures(fix.ConflictData)

        alice = User.query.filter_by(username=fix.UserData.alice.username).one()
        conflict = Conflict.query.get(fix.ConflictData.conflict_archived.id)
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
