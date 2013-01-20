import copy

from .models import TeamStatus

def censor_exchange(exchange, user):
    retval = []
    min_reveal = min(team_status.status['revealed'] for team_status in exchange)
    for team_status in exchange:
        # The status must be deepcopied so we don't modify the original list.
        status_to_censor = copy.deepcopy(team_status.status)
        if team_status.team not in user.teams:
            for i in range(min_reveal, len(status_to_censor['script'])):
                status_to_censor['script'][i] = u'<redacted>'
        retval.append(TeamStatus(team_status.team, status_to_censor))
    return retval

def censor_conflict_history(conflict_history, user):
    return [censor_exchange(exchange, user) for exchange in conflict_history]

def censor_allowed_actions(actions, user):
    retval = []
    for team_pair in actions:
        # This is a bit awkward; we have to have a copy of the team/actions list.
        # And also a copy of the actions list in that list.
        # But we can't deepcopy the list because it has a Team object in it
        to_censor = team_pair[:]
        to_censor[1] = copy.deepcopy(team_pair[1])
        if to_censor[0] not in user.teams and 'change-actions' in to_censor[1]:
            to_censor[1].remove('change-actions')
        retval.append(to_censor)
    return retval
