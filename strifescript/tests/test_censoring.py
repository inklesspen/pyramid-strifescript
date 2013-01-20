import transaction

import pytest

from nose import tools as nt

from ..models import DBSession, User, Conflict, Team, SetScriptEvent, NoResultFound
from .. import views, validation, models, acl, censoring

from . import BaseTest
from . import fixtures as fix

from mock import MagicMock, patch, create_autospec

class TestCensorExchange(BaseTest):
    def test_pc_team(self):
        self.add_fixtures(fix.conflict_with_changes.ConflictData)
        conflict = Conflict.query.get(fix.conflict_with_changes.ConflictData.conflict_with_event_changes.id)
        npc_team = Team.query.filter_by(conflict=conflict, name=u"NPC Team").one()
        pc_team = Team.query.filter_by(conflict=conflict, name=u"PC Team").one()

        raw = conflict.generate_history()
        exchange = raw[0]
        actual = censoring.censor_exchange(exchange, pc_team)
        expected = {
            npc_team.id: {
                'script': [
                    [u'action 1'],
                    [u'action 2', 'action 3'],
                    u'<redacted>'
                ],
                'revealed': 2
            },
            pc_team.id: {
                'script': [
                    [u'action 6'],
                    [u'replacement action 8'],
                    [u'replacement action 10']
                ],
                'revealed': 2
            }
        }

        assert expected == actual

    def test_npc_team(self):
        self.add_fixtures(fix.conflict_with_changes.ConflictData)
        conflict = Conflict.query.get(fix.conflict_with_changes.ConflictData.conflict_with_event_changes.id)
        npc_team = Team.query.filter_by(conflict=conflict, name=u"NPC Team").one()
        pc_team = Team.query.filter_by(conflict=conflict, name=u"PC Team").one()

        raw = conflict.generate_history()
        exchange = raw[0]
        actual = censoring.censor_exchange(exchange, npc_team)
        expected = {
            npc_team.id: {
                'script': [
                    [u'action 1'],
                    [u'action 2', u'action 3'],
                    [u'action 4', u'action 5']
                ],
                'revealed': 2
            },
            pc_team.id: {
                'script': [
                    [u'action 6'],
                    [u'replacement action 8'],
                    u'<redacted>'
                ],
                'revealed': 2
            }
        }

        assert expected == actual

class TestCensorActions(BaseTest):
    def test_simple_case(self):
        self.add_fixtures(fix.bare_conflict.ConflictData)
        alice = User.query.filter_by(username=fix.users.UserData.alice.username).one()
        claire = User.query.filter_by(username=fix.users.UserData.claire.username).one()
        npc_team = Team.query.get(1)
        pc_team = Team.query.get(2)

        actions = [
            [npc_team, ['set-script']],
            [pc_team, ['set-script']]
        ]

        assert actions == censoring.censor_allowed_actions(actions, alice)
        assert actions == censoring.censor_allowed_actions(actions, claire)

        actions = [
            [npc_team, ['reveal-volley', 'change-actions']],
            [pc_team, ['reveal-volley', 'change-actions']]
        ]

        expected = [
            [npc_team, ['reveal-volley', 'change-actions']],
            [pc_team, ['reveal-volley']]
        ]

        assert alice in npc_team.users and alice not in pc_team.users
        assert expected == censoring.censor_allowed_actions(actions, alice)

        expected = [
            [npc_team, ['reveal-volley']],
            [pc_team, ['reveal-volley', 'change-actions']]
        ]

        assert claire in pc_team.users and claire not in npc_team.users
        actual = censoring.censor_allowed_actions(actions, claire)
        assert expected == actual
