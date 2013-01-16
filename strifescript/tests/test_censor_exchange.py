import unittest
import transaction

from nose import tools as nt

from ..models import DBSession, User, Conflict, Team, SetScriptEvent, NoResultFound
from .. import views, validation, models, acl, censoring

from . import BaseTest
from . import fixtures as fix

from mock import MagicMock, patch, create_autospec

class TestCensorExchange(BaseTest):
    def test_pc_team(self):
        self.add_fixtures(fix.ConflictData)

        conflict = Conflict.query.get(fix.ConflictData.conflict_with_event_changes.id)
        npc_team = Team.query.get(fix.TeamData.npc_team.id)
        pc_team = Team.query.get(fix.TeamData.pc_team.id)

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
        self.add_fixtures(fix.ConflictData)

        conflict = Conflict.query.get(fix.ConflictData.conflict_with_event_changes.id)
        npc_team = Team.query.get(fix.TeamData.npc_team.id)
        pc_team = Team.query.get(fix.TeamData.pc_team.id)

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
