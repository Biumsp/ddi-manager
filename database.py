from logging_setup import logger, ERROR, OK
from json import loads, dumps
from datetime import datetime
import os


class Database():
    def __init__(self, path, file_name=None):

        # Initialize
        self.path = path
        self.id   = 0
        self.data = {}
        self.changes = {"add": [], "remove": []}
        self.pulled  = 0
        self.updated = 1
        self.pushed  = 0
        self.sent    = 0
        self.user = ''
        
        if file_name:
            # Load specified version
            error = self.get_version(file_name)
        else:
            # Load latest version
            error = self.get_last_local_version()
        if error:
            return ERROR     

         
    def set_user(self, user):
        self.user = user


    def just_pulled(self):
        self.pulled = 1
        self.get_last_local_version()


    def just_updated(self):
        self.updated = 1
        self.pushed  = 0
        self.sent    = 0
    

    def just_pushed(self):
        self.pushed = 1

    
    def just_sent(self):
        self.sent = 1
        self.data["sent"] = 1


    def just_added(self):
        self.updated = 0

    def just_removed(self):
        self.updated = 0


    def just_restored(self):
        self.updated = 1

    
    def restore(self):
        self.changes = {}

    
    def get_version(self, filename):
        try:
            with open(self.path + filename, "r") as file:
                v = loads(file.read()) 

            self.data = v
            self.id = self.data["id"] # Update the current ID

            # Update the state
            if self.data["sent"]:
                self.sent = 1

        except FileNotFoundError:
            logger.critical(f"invalid name {filename} for local database")
            return ERROR


    def get_last_local_version(self):
        try:
            v = str(max([int(x.split(".")[0]) for x in os.listdir(self.path)]))

            try:
                with open(self.path + v + ".json", "r") as file:
                    v = loads(file.read()) 

                self.data = v
                self.id   = self.data["id"] # Update the current ID

                # Update the state
                if self.data["sent"]:
                    self.sent = 1


            except FileNotFoundError:
                logger.critical(f"invalid name {v} for local database")
                return ERROR

        except FileNotFoundError:
            logger.critical(f"directory {path} is non-existent")
            return ERROR   


    def add(self, s):
        if s in self.data["ddi"]:
            logger.error(f"the student {s} is already in the list")
            return ERROR

        elif s in self.changes["add"]:
            logger.error(f"the student {s} was already added")
            return ERROR

        elif s in self.changes["remove"]:
            self.changes["remove"].remove(s)
            logger.info(f"reverting the action 'remove -n {s[0]} -c {s[1]}'")
            

        else:
            self.changes["add"].append(s)
            logger.info(f"adding the student {s[0]} - {s[1]}")

        self.just_added()
            
        
    def remove(self, s):
        if s not in self.changes["add"]:
            self.changes["add"].remove(s)
            logger.info(f"reverting the action 'add -n {s[0]} -c {s[1]}'")
            

        elif s not in self.data["ddi"]:
            logger.error(f"the student {s[0]} - {s[1]} cannot be removed: is not in the list")
            return ERROR
            
        elif s in self.changes["remove"]:
            logger.error(f"the student {s[0]} - {s[1]} was already removed")
            return ERROR

        else:
            self.changes["remove"].append(s)
            logger.info(f"removing the student {s[0]} - {s[1]}")

        self.just_removed()
            

    def merge_changes(self):
        """Merges the changes dict with the data dict (applies the pending changes)"""

        # create a temporary merged dict, check if it's consistent.
        # If it is, update self.data

        tmp = {"teachers": self.data["teachers"], "classes": self.data["classes"], "ddi": {}}

        # Changes in the ddi-students' list
        for s in self.data["ddi"]:
            if s not in self.changes["remove"]:
                tmp["ddi"].append(s)

        for s in self.changes["add"]:
            tmp["ddi"].append(s)

        self.data = tmp
        
    
    def get_changes_from_last_sent(self):
        """Gets the changes between the last updated version (since you
        can't have called send() without first update()) and the last
        sent update"""

        files = os.listdir(self.path)
        files.sort(key=lambda x: int(x.split(".")[0]), reverse=True)

        for file in files:
            last_sent_version = Database(self.path, file)
            if last_sent_version.sent:
                break

        lsvddi = last_sent_version.data["ddi"]
        nowddi = self.data["ddi"]

        diff = []
        for c in list(lsvddi.keys()):
            if c not in list(nowddi.keys()) or set(nowddi[c]) != set(lsvddi[c]):
                diff.append(c)
        
        for c in list(nowddi.keys()):
            if c not in list(lsvddi.keys()):
                diff.append(c)

        return diff, OK


    def get_payload(self):
        """Returns the dict to store in the file"""

        id, error = self.get_time()
        if error:
            return None, ERROR

        error = self.merge_changes()
        if error:
            return None, ERROR

        id, error = get_time()
        if error:
            return None, ERROR

        self.id = id

        payload = {"id": self.id,
                   "sent": self.sent,
                   "author": self.user,
                   "teachers": self.data["teachers"],
                   "classes": self.data["classes"],
                   "ddi": self.data["ddi"]}

        return payload, OK


    def update(self):
        """Updates the local database history"""

        try:
            pl, error = self.get_payload()
            if error:
                return ERROR

            with open(self.path + self.id + ".json", "w") as file:
                file.write(dumps(pl))
            
            print(f"Updated to version {self.id}\n")
            self.just_updated()

        except FileNotFoundError:
            logger.critical(f"invalid name {v} for local database")
            return ERROR

    
    def send(self):
        """Sends the emails"""

        changes, error = self.get_changes_from_last_sent()
        if error:
            return ERROR

        print("sent")
        print(changes)
        
        self.just_sent()
        self.update()
        self.push()
    

    def push(self):
        """Pushes the local database history to the drive"""
        print("push")
        self.just_pushed()


    def pull(self):
        """Pulls the database history from the drive"""

        print("pull")
        self.just_pulled()

    
    def get_time(self):
    
        try:
            now = datetime.now()

            year   = str(now.year)
            month  = str(now.month)
            day    = str(now.day)
            hour   = str(now.hour)
            minute = str(now.minute)
            second = str(now.second)

            month  = "0"*(2-len(month))  + month
            day    = "0"*(2-len(day))    + day
            hour   = "0"*(2-len(hour))   + hour
            minute = "0"*(2-len(minute)) + minute
            second = "0"*(2-len(second)) + second
            
            return  year+month+day+hour+minute+second, OK

        except:
            logger.critical("undefined error in <Database.get_name>")
            return None, ERROR


    def list_class(self, c):
        if c not in self.data["classes"]:
            logger.error(f"the class {c} is non-existent")
            return ERROR
        
        else:
            message  = f"\nclass {c}:\n"
            self.data["classes"][c]["students"].sort()
            self.data["classes"][c]["teachers"].sort()

            spaces = max(len(name) for name in self.data["classes"][c]["students"])

            for s in self.data["classes"][c]["students"]:
                message += "+ {:^{spaces}}".format(s, spaces=spaces) 
                message += (s+"-"+c in self.data["ddi"])*" - DDI" + "\n"
            
            message += "\nteachers:\n"
            for t in self.data["classes"][c]["teachers"]:
                message += f"+ {t:22}\n" 
                
            print(message)


    def check_state(self, s: int):
        """Check if you can perform the action s on the basis of the states"""

        if s == "pull":
            # You can always pull
            return False, OK

        elif s == "add":
             # You can always add
            return False, OK

        elif s == "remove":
             # You can always remove
            return False, OK
        
        elif s == "list":
             # You can always list
            return False, OK
        
        elif s == "update":
            # You can update only if you just made changes
            if self.updated:
                logger.warning(f"nothing to update")
                return True, OK
            else:
                return False, OK                
        
        elif s == "push":
            # You can push only if you kust upated
            if self.updated:
                if self.pushed:
                    logger.warning(f"you have already pushed")
                    return True, OK
                else:
                    return False, OK
            else:
                logger.warning(f"you have to update first")
                return True, OK
            
        elif s == "send":
            # You can send only if you both pulled and updated
            if self.pulled:
                if self.updated:
                    if self.sent:
                        logger.warning(f"you have already sent the last update")
                        return True, OK
                    else:
                        return False, OK
                else:
                    logger.warning(f"you have to update first")
                    return True, OK
            else:
                logger.warning(f"you have to pull first")
                return True, OK
        
        elif s == "restore":
            if self.updated:
                logger.warning(f"no changes were made")
                return True, OK
            else:
                return False, OK

        else:
            logger.critical(f"invalid action {s} passed to <check_state>")
            return None, ERROR