import copy

def censor_exchange(exchange, team):
    for team_id in exchange.keys():
        if team_id == team.id:
            continue

        team_val = exchange[team_id]
        revealed_count = team_val['revealed']
        for i in range(revealed_count, len(team_val['script'])):
            team_val['script'][i] = u'<redacted>'

    return exchange

def censor_conflict_history(conflict_history, team):
    return [censor_exchange(exchange, team) for exchange in conflict_history]

def censor_allowed_actions(actions, user):
    retval = []
    for team_pair in actions:
        # This is a bit awkward; we have to have a copy of the team/actions list.
        # And also a copy of the actions list in that list.
        to_censor = team_pair[:]
        to_censor[1] = team_pair[1][:]
        if to_censor[0] not in user.teams and 'change-actions' in to_censor[1]:
            to_censor[1].remove('change-actions')
        retval.append(to_censor)
    return retval
