import transaction

import pytest

from nose import tools as nt

from ..models import DBSession, User, Conflict, Team, SetScriptEvent, NoResultFound
from .. import views, validation, models, acl

from . import BaseTest
from . import fixtures as fix

from mock import MagicMock, patch, create_autospec

# Let's start with constructing history out of the event log
class TestConflictHistory(BaseTest):
    def test(self):
        self.add_fixtures(fix.conflict_with_scripts.ConflictData)
        conflict = Conflict.query.get(fix.conflict_with_scripts.ConflictData.conflict_with_both_scripts.id)
        npc_team = Team.query.get(fix.conflict_with_scripts.TeamData.npc_team.id)
        pc_team = Team.query.get(fix.conflict_with_scripts.TeamData.pc_team.id)

        expected = [
            {
                npc_team.id: {
                    'script': [
                        ['action 1'],
                        ['action 2', 'action 3'],
                        ['action 4', 'action 5']
                    ],
                    'revealed': 2
                },
                pc_team.id: {
                    'script': [
                        ['action 6'],
                        ['action 7', 'action 8'],
                        ['action 9', 'action 10']
                    ],
                    'revealed': 1
                }
            }
        ]
        actual = conflict.generate_history()

        assert expected == actual

    def test_with_changed_events(self):
        self.add_fixtures(fix.conflict_with_changes.ConflictData)
        conflict = Conflict.query.get(fix.conflict_with_changes.ConflictData.conflict_with_event_changes.id)
        npc_team = Team.query.get(fix.conflict_with_changes.TeamData.npc_team.id)
        pc_team = Team.query.get(fix.conflict_with_changes.TeamData.pc_team.id)

        expected = [
            {
                npc_team.id: {
                    'script': [
                        ['action 1'],
                        ['action 2', 'action 3'],
                        ['action 4', 'action 5']
                    ],
                    'revealed': 2
                },
                pc_team.id: {
                    'script': [
                        ['action 6'],
                        ['replacement action 8'],
                        ['replacement action 10']
                    ],
                    'revealed': 2
                }
            }
        ]

        actual = conflict.generate_history()

        assert expected == actual

class TestConflictActions(BaseTest):
    def get_bare_conflict(self):
        self.add_fixtures(fix.bare_conflict.ConflictData)
        conflict = Conflict.query.get(fix.bare_conflict.ConflictData.conflict.id)
        return conflict

    def test_bare_conflict(self):
        conflict = self.get_bare_conflict()
        npc_team = Team.query.filter_by(conflict=conflict, name=u"NPC Team").one()
        pc_team = Team.query.filter_by(conflict=conflict, name=u"PC Team").one()

        actual = conflict.allowed_actions()
        expected = {
            npc_team: ['set-script'],
            pc_team: ['set-script'],
        }

        assert expected == actual

    def get_with_one_script(self):
        conflict = self.get_bare_conflict()
        npc_team = Team.query.filter_by(conflict=conflict, name=u"NPC Team").one()

        sse = SetScriptEvent(user=npc_team.users[0], team=npc_team, conflict=conflict, exchange=1)
        sse.volley_1 = ['action 1']
        sse.volley_2 = ['action 2', 'action 3']
        sse.volley_3 = ['action 4', 'action 5']
        conflict.events.append(sse)
        return conflict

    def test_with_one_script(self):
        conflict = self.get_with_one_script()
        npc_team = Team.query.filter_by(conflict=conflict, name=u"NPC Team").one()
        pc_team = Team.query.filter_by(conflict=conflict, name=u"PC Team").one()

        actual = conflict.allowed_actions()
        expected = {
            npc_team: [],
            pc_team: ['set-script'],
        }

        assert expected == actual

    def get_with_both_scripts(self):
        conflict = self.get_with_one_script()
        pc_team = Team.query.filter_by(conflict=conflict, name=u"PC Team").one()

        sse = SetScriptEvent(user=pc_team.users[0], team=pc_team, conflict=conflict, exchange=1)
        sse.volley_1 = ['action 6']
        sse.volley_2 = ['action 7', 'action 8']
        sse.volley_3 = ['action 9', 'action 10']
        conflict.events.append(sse)
        return conflict

    @pytest.mark.xfail
    def test_with_both_scripts(self):
        conflict = self.get_with_both_scripts()
        npc_team = Team.query.filter_by(conflict=conflict, name=u"NPC Team").one()
        pc_team = Team.query.filter_by(conflict=conflict, name=u"PC Team").one()

        actual = conflict.allowed_actions()
        expected = {
            npc_team: ['reveal-volley', 'change-action'],
            pc_team: ['reveal-volley', 'change-action'],
        }

        assert expected == actual
