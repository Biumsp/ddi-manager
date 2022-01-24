USERS = {"bus": "111"}

def authenticate(username, password):
    return (username in USERS and password == USERS[username])