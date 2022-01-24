from pandas import read_excel
import logging
from json import dumps, loads
from time import sleep
from dispatcher import Dispatcher
from handlers import update, push, pull, send, status, check, restore
from getpass import getpass
from authentication import authenticate


if __name__ == '__main__':

    while 1:
        username = input("Username: ")
        password = getpass()

        if authenticate(username, password):
            break
        else:
            print("Wrong credentials\n")
        
    print()


    dispatcher = Dispatcher()

    dispatcher.add_handler("update", update, ["-h", "--help", "-i", "--info"], "update the local database",
                           ["info about this command", "info about this command",
                            "change loglevel to INFO", "change loglevel to INFO"])

    dispatcher.add_handler("push", push, ["-h", "--help", "-i", "--info"], "push changes to the remote database",
                           ["info about this command", "info about this command",
                            "change loglevel to INFO", "change loglevel to INFO"])

    dispatcher.add_handler("pull", pull, ["-h", "--help", "-i", "--info"], "pull changes from the remote database",
                           ["info about this command", "info about this command",
                            "change loglevel to INFO", "change loglevel to INFO"])

    dispatcher.add_handler("send", send, ["-h", "--help", "-i", "--info", "-f", "--force", "-a", "--all"],
                           "notify the teachers of the DDI students in their classrooms",
                           ["info about this command", "info about this command",
                            "change loglevel to INFO", "change loglevel to INFO",
                            "send again the latest update", "send again the latest update",
                            "send the email to all the teachers", "send the email to all the teachers"])

    dispatcher.add_handler("status", status, ["-h", "--help", "-i", "--info", "-f", "--file", "-d", "--detailed"], 
                            "return the DDI overall status",
                            ["info about this command", "info about this command",
                            "change loglevel to INFO", "change loglevel to INFO",
                            "save the output to a file", "save the output to a file",
                            "show all details", "show all details"])

    dispatcher.add_handler("check", check, ["-h", "--help", "-i", "--info"], "check if the names match",
                           ["info about this command", "info about this command",
                            "change loglevel to INFO", "change loglevel to INFO"])

    dispatcher.add_handler("restore", restore, ["-h", "--help", "-i", "--info"], 
                           "restore a specific state from the database",
                           ["info about this command", "info about this command",
                            "change loglevel to INFO", "change loglevel to INFO"])

    while 1:

        inps  = input(">> ").split()

        if inps:
            cmd = inps[0]
            opts = [x for x in inps[1:] if '-' in x]
            args = [x for x in inps[1:] if '-' not in x]

            dispatcher.dispatch(cmd, args, opts)