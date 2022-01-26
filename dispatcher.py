from handlers import update, push, pull, send, status, check, restore
from logging_setup import logger

class Dispatcher():
    def __init__(self):
        self.handlers = {}
        
    
    def add_handler(self, key: str, 
                    handler, 
                    opts: list = [], 
                    info: str = '',
                    opts_info: list = []):

        if not opts_info:
            opts_info = ["" for _ in opts]

        self.handlers.update({key: {"handler": handler, 
                                    "opts": opts, 
                                    "info": info, 
                                    "opts_info": opts_info} })


    def dispatch(self, cmd, args, opts, database):
        if cmd not in self.handlers:
            self._invalid_cmd(cmd)
            return
        
        for opt in opts:
            if opt not in self.handlers[cmd]["opts"]:
                self._invalid_opt(cmd, opt)
                return

        handler = self.handlers[cmd]["handler"]
        handler(args, opts, database)


    def _invalid_cmd(self, cmd):
        logger.error(f"invalid command {cmd}\n")

        print("The available commands are:\n")
        for c in self.handlers.keys():
            print(f"{c:9} {self.handlers[c]['info']}")
        print()

    
    def _invalid_opt(self, cmd, opt):
        logger.error(f"invalid option {opt} for command {cmd}\n")

        print(f"The available options for {cmd} are:\n")
        for opt, info in zip(self.handlers[cmd]["opts"], self.handlers[cmd]["opts_info"]):
            print(f"{opt:9} {info}")
        print()


dispatcher = Dispatcher()

dispatcher.add_handler("pull", pull, ["-h", "--help", "-i", "--info"], 
                        "pull changes from the remote database",
                        ["info about this command", "info about this command",
                        "change loglevel to INFO", "change loglevel to INFO"])

dispatcher.add_handler("add", add, ["-h", "--help", "-i", "--info"], 
                        "add a student to the list of DDI students",
                        ["info about this command", "info about this command",
                        "change loglevel to INFO", "change loglevel to INFO"])

dispatcher.add_handler("remove", remove, ["-h", "--help", "-i", "--info"], 
                        "remove a student from the list of DDI students",
                        ["info about this command", "info about this command",
                        "change loglevel to INFO", "change loglevel to INFO"])

dispatcher.add_handler("update", update, ["-h", "--help", "-i", "--info"], 
                        "update the local database",
                        ["info about this command", "info about this command",
                        "change loglevel to INFO", "change loglevel to INFO"])

dispatcher.add_handler("push", push, ["-h", "--help", "-i", "--info"],
                        "push changes to the remote database",
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

dispatcher.add_handler("list", list_class, ["-h", "--help", "-i", "--info"], 
                        "list the students of a class",
                        ["info about this command", "info about this command",
                        "change loglevel to INFO", "change loglevel to INFO"])