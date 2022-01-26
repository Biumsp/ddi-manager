from getpass import getpass

USERS = {"bus": "111"}

def authenticate():
    while 1:
        username = input("Username: ")
        password = getpass()

        if (username in USERS and password == USERS[username]):
            break
        else:
            logger.error("wrong credentials\n")
    
    return username