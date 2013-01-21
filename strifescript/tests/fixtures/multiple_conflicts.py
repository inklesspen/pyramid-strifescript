from fixture import DataSet

from .users import UserData

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
    class alpha_team:
        id = 3
        name = u"Alpha"
        users = [UserData.alice, UserData.bob]
    class aleph_team:
        id = 4
        name = u"Aleph"
        users = [UserData.claire]
    class a_team:
        id = 5
        name = u"A"
        users = [UserData.danny]

class ConflictData(DataSet):
    class conflict:
        id = 1
        name = u"The Glorious Battle"
        teams = [TeamData.npc_team, TeamData.pc_team]
    class second_conflict:
        id = 2
        name = u"Three-way"
        teams = [TeamData.alpha_team, TeamData.aleph_team, TeamData.a_team]
