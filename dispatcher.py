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

    def dispatch(self, cmd, args, opts):
        if cmd not in self.handlers:
            self._invalid_cmd(cmd)
            return
        
        for opt in opts:
            if opt not in self.handlers[cmd]["opts"]:
                self._invalid_opt(cmd, opt)
                return

        handler = self.handlers[cmd]["handler"]
        handler(args, opts)


    def _invalid_cmd(self, cmd):
        print(f"ERROR - invalid command {cmd}\n")

        print("The available commands are:\n")
        for c in self.handlers.keys():
            print(f"{c:9} {self.handlers[c]['info']}")
        print()

    
    def _invalid_opt(self, cmd, opt):
        print(f"ERROR - invalid option {opt} for command {cmd}\n")

        print(f"The available options for {cmd} are:\n")
        for opt, info in zip(self.handlers[cmd]["opts"], self.handlers[cmd]["opts_info"]):
            print(f"{opt:9} {info}")
        print()