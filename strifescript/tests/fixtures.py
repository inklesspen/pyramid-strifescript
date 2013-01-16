from ..models import User

from fixture import DataSet

class UserData(DataSet):
    class foo_user:
        username = u"foo"
        email = u"foo@example.com"
        _password = "foofoofoo"
        password_hash = User.generate_password_hash(_password, difficulty=2)
    class alice:
        username = u"alice"
        email = u"alice@example.com"
        _password = "alice's password"
        password_hash = User.generate_password_hash(_password, difficulty=2)
    class bob:
        username = u"bob"
        email = u"bob@example.com"
        _password = "bob's password"
        password_hash = User.generate_password_hash(_password, difficulty=2)
    class claire:
        username = u"claire"
        email = u"claire@example.com"
        _password = "claire's password"
        password_hash = User.generate_password_hash(_password, difficulty=2)
    class danny:
        username = u"danny"
        email = u"danny@example.com"
        _password = "danny's password"
        password_hash = User.generate_password_hash(_password, difficulty=2)

class TeamData(DataSet):
    class npc_team:
        id = 1
        name = u"NPC Team"
        users = [UserData.alice]
        notes = u"Balrogs and Goblins, oh my"
    class pc_team:
        id = 2
        name = u"PC Team"
        users = [UserData.bob, UserData.claire, UserData.danny]

class SetScriptEventData(DataSet):
    class npc_script:
        user = UserData.alice
        team = TeamData.npc_team
        exchange = 1
        volley_1_array = u'action 1'
        volley_2_array = u'action 2_action 3'
        volley_3_array = u'action 4_action 5'
    class pc_script:
        user = UserData.claire
        team = TeamData.pc_team
        exchange = 1
        volley_1_array = u'action 6'
        volley_2_array = u'action 7_action 8'
        volley_3_array = u'action 9_action 10'

class RevealVolleyEventData(DataSet):
    class npc_reveal_1:
        user = UserData.alice
        team = TeamData.npc_team
        exchange = 1
    class npc_reveal_2:
        user = UserData.alice
        team = TeamData.npc_team
        exchange = 1
    class npc_reveal_3:
        user = UserData.alice
        team = TeamData.npc_team
        exchange = 1
    class pc_reveal_1:
        user = UserData.bob
        team = TeamData.pc_team
        exchange = 1
    class pc_reveal_2:
        user = UserData.bob
        team = TeamData.pc_team
        exchange = 1
    class pc_reveal_3:
        user = UserData.claire
        team = TeamData.pc_team
        exchange = 1

class ChangeActionsEventData(DataSet):
    class pc_change_2:
        user = UserData.bob
        team = TeamData.pc_team
        exchange = 1
        volley_no = 2
        forfeited_action = u'action 7'
        changed_action = u'action 8'
        replacement_action = u'replacement action 8'
    class pc_change_3:
        user = UserData.bob
        team = TeamData.pc_team
        exchange = 1
        volley_no = 3
        forfeited_action = u'action 9'
        changed_action = u'action 10'
        replacement_action = u'replacement action 10'

class ConflictData(DataSet):
    class conflict:
        id = 1
        name = u"The Glorious Battle"
        teams = [TeamData.npc_team, TeamData.pc_team]
    class conflict_archived(conflict):
        id = 2
        archived = True
    class conflict_with_both_scripts(conflict):
        id = 3
        events = [
            SetScriptEventData.npc_script, SetScriptEventData.pc_script,
            RevealVolleyEventData.npc_reveal_1, RevealVolleyEventData.pc_reveal_1,
            RevealVolleyEventData.npc_reveal_2
        ]
    class conflict_with_event_changes(conflict):
        id = 4
        events = [
            SetScriptEventData.npc_script, SetScriptEventData.pc_script,
            RevealVolleyEventData.npc_reveal_1, RevealVolleyEventData.pc_reveal_1,
            ChangeActionsEventData.pc_change_2,
            RevealVolleyEventData.npc_reveal_2, RevealVolleyEventData.pc_reveal_2,
            ChangeActionsEventData.pc_change_3,
        ]
    class conflict_with_both_scripts_fully_revealed(conflict):
        id = 5
        events = [
            SetScriptEventData.npc_script, SetScriptEventData.pc_script,
            RevealVolleyEventData.npc_reveal_1, RevealVolleyEventData.pc_reveal_1,
            RevealVolleyEventData.npc_reveal_2, RevealVolleyEventData.pc_reveal_2,
            RevealVolleyEventData.npc_reveal_3, RevealVolleyEventData.pc_reveal_3,
        ]
