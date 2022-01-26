from logging_setup import logger, log_level_default
from dispatcher import dispatcher
from database import Database
from authentication import authenticate
from sys import argv

def unpack_input(inps):
    cmd = inps[0]
    args = [x for x in inps[1:] if '-' not in x]
    opts = [x for x in inps[1:] if '-' in x]

    return cmd, args, opts


if __name__ == '__main__':

    # Authentication 
    #user = authenticate()
    user = "bus"

    # Load database
    database = Database("database\\")
    database.set_user(user)

    # Main Loop ---------------------------------
    while 1:
        # Reset the logging level
        logger.setLevel(log_level_default)

        # Get the user input
        inps  = input(">> ").split()
        if inps:
            cmd, args, opts = unpack_input(inps)
            dispatcher.dispatch(cmd, args, opts, database)

    # -------------------------------------------