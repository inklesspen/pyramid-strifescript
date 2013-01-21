import json, pytest

from nose import tools as nt

from pyramid import testing

from ..models import DBSession, User, Conflict, Team, NoResultFound
from ..models import TeamStatus, TeamActions
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

        assert conflict.id == actual['id']
        assert conflict.name == actual['name']
        
        expected_teams = [
                {
                    'id': npc_team.id,
                    'name': npc_team.name,
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
            ]
        assert expected_teams == actual['teams']

        expected_action_choices = [
            TeamActions(npc_team, ['set-script']),
            TeamActions(pc_team, ['set-script'])
        ]

        assert expected_action_choices == actual['action_choices']

        expected_exchanges = []
        assert expected_exchanges == actual['exchanges']

    def test_conflict_with_scripts(self):
        self.add_fixtures(fix.conflict_with_scripts.ConflictData)
        alice = User.query.filter_by(username=fix.users.UserData.alice.username).one()

        conflict = Conflict.query.get(fix.conflict_with_scripts.ConflictData.conflict.id)

        npc_team = Team.query.filter_by(conflict=conflict, name=u"NPC Team").one()
        pc_team = Team.query.filter_by(conflict=conflict, name=u"PC Team").one()

        request = testing.DummyRequest(method='GET', current_user=alice, matchdict=dict(id=conflict.id))
        request.context = acl.Conflict(request)
        actual = views.conflict_info(request)

        assert conflict.id == actual['id']
        assert conflict.name == actual['name']
        
        expected_teams = [
                {
                    'id': npc_team.id,
                    'name': npc_team.name,
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
            ]
        assert expected_teams == actual['teams']

        # Alice is on the NPC team; she shouldn't see that the PC team can change actions
        expected_action_choices = [
            TeamActions(npc_team, ['reveal-volley', 'change-actions']),
            TeamActions(pc_team, ['reveal-volley'])
        ]

        assert expected_action_choices == actual['action_choices']

        # But let's make sure that's actually a choice the PC team has:
        assert 'change-actions' in conflict.allowed_actions()[pc_team]

        expected_exchanges = [
            [
                TeamStatus(npc_team,
                 {'revealed': 0,
                  'script': [[u'action 1'],
                             [u'action 2', u'action 3'],
                             [u'action 4', u'action 5']]}),
                TeamStatus(pc_team,
                 {'revealed': 0,
                  'script': [u'<redacted>', u'<redacted>', u'<redacted>']})]]

        assert expected_exchanges == actual['exchanges']

class TestConflictAction(BaseTest):
    def test_set_script(self):
        self.add_fixtures(fix.bare_conflict.ConflictData)

        alice = User.query.filter_by(username=fix.users.UserData.alice.username).one()
        conflict = Conflict.query.get(fix.bare_conflict.ConflictData.conflict.id)
        npc_team = Team.query.filter_by(conflict=conflict, name=u"NPC Team").one()
        pc_team = Team.query.filter_by(conflict=conflict, name=u"PC Team").one()

        request_body = {
            'action': 'set-script',
            'team': npc_team.id,
            'script': [['action 1'], ['action 2', 'action 3'], ['action 4', 'action 5']]
        }
        request_body = json.loads(json.dumps(request_body))
        request = testing.DummyRequest(json_body=request_body, method='POST', current_user=alice, matchdict=dict(id=conflict.id))
        request.context = acl.Conflict(request)
        actual = views.conflict_action(request)
        assert {} == actual

        conflict = Conflict.query.get(fix.bare_conflict.ConflictData.conflict.id)
        assert len(conflict.events) == 1

        expected = [TeamStatus(npc_team,
                     {'revealed': 0,
                      'script': [[u'action 1'],
                                 [u'action 2', u'action 3'], 
                                 [u'action 4', u'action 5']]}),
                    TeamStatus(pc_team,
                     {'revealed': 0})]

        assert expected == conflict.generate_history()[0]

    def test_reveal_volley(self):
        self.add_fixtures(fix.conflict_with_scripts.ConflictData)
        alice = User.query.filter_by(username=fix.users.UserData.alice.username).one()
        conflict = Conflict.query.get(fix.conflict_with_scripts.ConflictData.conflict.id)
        npc_team = Team.query.filter_by(conflict=conflict, name=u"NPC Team").one()
        pc_team = Team.query.filter_by(conflict=conflict, name=u"PC Team").one()

        request_body = {
            'action': 'reveal-volley',
            'team': npc_team.id
        }
        request_body = json.loads(json.dumps(request_body))
        request = testing.DummyRequest(json_body=request_body, method='POST', current_user=alice, matchdict=dict(id=conflict.id))
        request.context = acl.Conflict(request)
        actual = views.conflict_action(request)
        assert {} == actual

        conflict = Conflict.query.get(fix.conflict_with_scripts.ConflictData.conflict.id)
        assert len(conflict.events) == 3

        expected = [TeamStatus(npc_team,
                     {'revealed': 1,
                      'script': [[u'action 1'],
                                 [u'action 2', u'action 3'], 
                                 [u'action 4', u'action 5']]}),
                    TeamStatus(pc_team,
                     {'revealed': 0,
                      'script': [[u'action 6'],
                                 [u'action 7', u'action 8'],
                                 [u'action 9', u'action 10']]})]

        assert expected == conflict.generate_history()[0]

    def test_change_actions(self):
        self.add_fixtures(fix.conflict_with_scripts.ConflictData)

        alice = User.query.filter_by(username=fix.users.UserData.alice.username).one()
        claire = User.query.filter_by(username=fix.users.UserData.claire.username).one()
        conflict = Conflict.query.get(fix.conflict_with_scripts.ConflictData.conflict.id)
        npc_team = Team.query.filter_by(conflict=conflict, name=u"NPC Team").one()
        pc_team = Team.query.filter_by(conflict=conflict, name=u"PC Team").one()

        request_body = {
            'action': 'change-actions',
            'team': npc_team.id,
            'volley_no': 2,
            'forfeited_action': u'action 2',
            'changed_action': u'action 3',
            'replacement_action': u'changed'
        }
        request_body = json.loads(json.dumps(request_body))
        request = testing.DummyRequest(json_body=request_body, method='POST', current_user=alice, matchdict=dict(id=conflict.id))
        request.context = acl.Conflict(request)
        actual = views.conflict_action(request)
        assert {} == actual

        conflict = Conflict.query.get(fix.conflict_with_scripts.ConflictData.conflict.id)
        assert len(conflict.events) == 3

        expected = [TeamStatus(npc_team,
                     {'revealed': 0,
                      'script': [[u'action 1'],
                                 [u'changed'], 
                                 [u'action 4', u'action 5']]}),
                    TeamStatus(pc_team,
                     {'revealed': 0,
                      'script': [[u'action 6'],
                                 [u'action 7', u'action 8'],
                                 [u'action 9', u'action 10']]})]

        assert expected[0] == conflict.generate_history()[0][0]

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

