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
        name = u"NPC Team"
        users = [UserData.alice]
        notes = u"Balrogs and Goblins, oh my"
    class pc_team:
        name = u"PC Team"
        users = [UserData.bob, UserData.claire, UserData.danny]

class ConflictData(DataSet):
    class conflict:
        id = 1
        name = u"The Glorious Battle"
        teams = [TeamData.npc_team, TeamData.pc_team]
    class conflict_archived(conflict):
        id = 2
        archived = True
