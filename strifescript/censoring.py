import copy

from .models import TeamStatus, TeamActions

def censor_exchange(exchange, user):
    retval = []
    min_reveal = min(team_status.status['revealed'] for team_status in exchange)
    for team_status in exchange:
        # The status must be deepcopied so we don't modify the original list.
        status_to_censor = copy.deepcopy(team_status.status)
        if team_status.team not in user.teams and 'script' in status_to_censor:
            for i in range(min_reveal, len(status_to_censor['script'])):
                status_to_censor['script'][i] = u'<redacted>'
        retval.append(TeamStatus(team_status.team, status_to_censor))
    return retval

def censor_conflict_history(conflict_history, user):
    return [censor_exchange(exchange, user) for exchange in conflict_history]

def censor_allowed_actions(actions, user):
    retval = []
    for team_actions in actions:
        # The list of actions must be deepcopied so we don't modify the original.
        actions_to_censor = copy.deepcopy(team_actions.actions)
        if team_actions.team not in user.teams and 'change-actions' in actions_to_censor:
            actions_to_censor.remove('change-actions')
        retval.append(TeamActions(team_actions.team, actions_to_censor))
    return retval
