import requests, json

s = requests.Session()

base = "http://0.0.0.0:6543"
headers = {'content-type': 'application/json'}

def register(username, password, email=None):
    url = base + "/register"
    body = {
        'username': username,
        'password': password
    }
    if email is not None:
        body['email'] = email
    r = s.post(url, json.dumps(body), headers=headers)
    if r.status_code not in [requests.codes.ok, requests.codes.bad_request]:
        r.raise_for_status()
    return r.json()

def login(username, password):
    url = base + "/login"
    body = {
        'username': username,
        'password': password
    }
    r = s.post(url, json.dumps(body), headers=headers)
    if r.status_code not in [requests.codes.ok, requests.codes.bad_request]:
        r.raise_for_status()
    return r.json()

def logout():
    url = base + "/logout"
    r = s.post(url, headers=headers)
    if r.status_code not in [requests.codes.ok, requests.codes.bad_request]:
        r.raise_for_status()
    return r.json()

def construct_team(name, usernames, notes=None):
    t = {'name': name,
         'participants': usernames,
    }
    if notes is not None:
        t['notes'] = notes
    return t

def create_conflict(name, teams):
    url = base + "/conflict"
    body = {
        'name': name,
        'teams': teams
    }
    r = s.post(url, json.dumps(body), headers=headers)
    if r.status_code not in [requests.codes.ok, requests.codes.bad_request]:
        r.raise_for_status()
    return r.json()

def view_conflict(id):
    url = base + "/conflict/" + str(id)
    r = s.get(url, headers=headers)
    if r.status_code not in [requests.codes.ok, requests.codes.bad_request]:
        r.raise_for_status()
    return r.json()

def set_script(conflict_id, team_id, script):
    url = base + "/conflict/" + str(conflict_id) + "/action"
    body = {
        'action': 'set-script',
        'team': team_id,
        'script': script
    }
    r = s.post(url, json.dumps(body), headers=headers)
    if r.status_code not in [requests.codes.ok, requests.codes.bad_request]:
        r.raise_for_status()
    return r.json()
