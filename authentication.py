USERS = {"bussetti": "12345"}

def authenticate(username, password):
    return (username in USERS and password == USERS[username])