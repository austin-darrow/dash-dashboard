import json

with open('./assets/data/accounts.txt') as f:
    data = f.read()
    ACCOUNTS = json.loads(data)

def authenticate(username, password):
    if username is None or password is None:
        return False
    if username in ACCOUNTS.keys():
        if ACCOUNTS[username] == password:
            return True
    return False