import transaction

import pytest

from nose import tools as nt

from ..models import DBSession, User, Conflict, Team, SetScriptEvent, NoResultFound
from ..models import TeamStatus
from .. import views, validation, models, acl, censoring

from . import BaseTest
from . import fixtures as fix

from mock import MagicMock, patch, create_autospec

class TestCensorExchange(BaseTest):
    def test_for_pc_team(self):
        self.add_fixtures(fix.conflict_with_changes.ConflictData)
        conflict = Conflict.query.get(fix.conflict_with_changes.ConflictData.conflict_with_event_changes.id)
        alice = User.query.filter_by(username=fix.users.UserData.alice.username).one()
        claire = User.query.filter_by(username=fix.users.UserData.claire.username).one()
        npc_team = Team.query.filter_by(conflict=conflict, name=u"NPC Team").one()
        pc_team = Team.query.filter_by(conflict=conflict, name=u"PC Team").one()

        raw = conflict.generate_history()
        exchange = raw[0]
        assert claire not in npc_team.users and claire in pc_team.users
        actual = censoring.censor_exchange(exchange, claire)

        expected = [TeamStatus(npc_team,
                     {'revealed': 2,
                      'script': [[u'action 1'], [u'action 2', u'action 3'], u'<redacted>']}),
                    TeamStatus(pc_team,
                     {'revealed': 2,
                      'script': [[u'action 6'],
                                 [u'replacement action 8'],
                                 [u'replacement action 10']]})]

        assert expected == actual

    def test_for_npc_team(self):
        self.add_fixtures(fix.conflict_with_changes.ConflictData)
        conflict = Conflict.query.get(fix.conflict_with_changes.ConflictData.conflict_with_event_changes.id)
        alice = User.query.filter_by(username=fix.users.UserData.alice.username).one()
        claire = User.query.filter_by(username=fix.users.UserData.claire.username).one()
        npc_team = Team.query.filter_by(conflict=conflict, name=u"NPC Team").one()
        pc_team = Team.query.filter_by(conflict=conflict, name=u"PC Team").one()

        raw = conflict.generate_history()
        exchange = raw[0]
        assert alice not in pc_team.users and alice in npc_team.users
        actual = censoring.censor_exchange(exchange, alice)

        expected = [TeamStatus(npc_team,
                     {'revealed': 2,
                      'script': [[u'action 1'],
                                 [u'action 2', u'action 3'], 
                                 [u'action 4', u'action 5']]}),
                    TeamStatus(pc_team,
                     {'revealed': 2,
                      'script': [[u'action 6'],
                                 [u'replacement action 8'],
                                 u'<redacted>']})]

        assert expected == actual

    def test_with_uneven_reveals(self):
        self.add_fixtures(fix.conflict_with_reveals.ConflictData)
        # The NPC team has issued two reveals, but the PC team has only issued one.
        # The PC team cannot see the NPCs' second volley until they reveal theirs.

        conflict = Conflict.query.get(fix.conflict_with_reveals.ConflictData.conflict.id)
        alice = User.query.filter_by(username=fix.users.UserData.alice.username).one()
        claire = User.query.filter_by(username=fix.users.UserData.claire.username).one()
        npc_team = Team.query.filter_by(conflict=conflict, name=u"NPC Team").one()
        pc_team = Team.query.filter_by(conflict=conflict, name=u"PC Team").one()

        raw = conflict.generate_history()
        exchange = raw[0]

        for team_status in exchange:
            if team_status.team is npc_team:
                assert team_status.status['revealed'] == 2
            if team_status.team is pc_team:
                assert team_status.status['revealed'] == 1

        assert claire in pc_team.users and claire not in npc_team.users
        actual = censoring.censor_exchange(exchange, claire)

        expected = [
            TeamStatus(npc_team,
                       {'revealed': 2,
                        'script': [[u'action 1'], u'<redacted>', u'<redacted>']}),
            TeamStatus(pc_team,
                       {'revealed': 1,
                        'script': [[u'action 6'],
                                   [u'action 7', u'action 8'],
                                   [u'action 9', u'action 10']]})
        ]

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
