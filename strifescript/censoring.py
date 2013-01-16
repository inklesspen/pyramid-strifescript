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
