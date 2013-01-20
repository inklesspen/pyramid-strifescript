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

def censor_allowed_actions(actions, team):
    retval = {}
    for team_id in actions.keys():
        retval[team_id] = actions[team_id][:]
        if team.id != team_id and 'change-actions' in retval[team_id]:
            retval[team_id].remove('change-actions')
    return retval
