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

class ConflictData(DataSet):
    class conflict:
        id = 1
        name = u"The Glorious Battle"
        teams = [TeamData.npc_team, TeamData.pc_team]
