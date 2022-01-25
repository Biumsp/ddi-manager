from logging_setup import logger, ERROR, OK
from json import loads, dumps
from datetime import datetime
from colorout import blue, green, red
import os


class Database():
    def __init__(self, path, file_name=None):

        # Initialize
        self.path = path
        self.id   = 0
        self.data = {}
        self.changes = {}
        self.pulled  = 0
        self.updated = 1
        self.pushed  = 0
        self.sent    = 0
        self.user = ''
        
        if file_name:
            # Load specified version
            error = self.get_version(filename)
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


    def just_changed(self):
        self.updated = 0


    def just_restored(self):
        self.updated = 1

    
    def restore(self):
        self.changes = {}

    
    def get_version(self, filename):
        try:
            with open(path + filename + ".json", "r") as file:
                v = loads(file.read()) 

            self.data = v
            self.id = self.data["id"] # Update the current ID

            # Update the state
            if self.data["sent"]:
                self.state = STATE_SEND

            return OK

        except FileNotFoundError:
            logging.critical(f"invalid name {v} for local database")
            return ERROR


    def get_last_local_version(self):
        try:
            v = str(max([int(x.split(".")[0]) for x in os.listdir(self.path)]))

            try:
                with open(path + v + ".json", "r") as file:
                    v = loads(file.read()) 

                self.data = v
                self.id   = self.data["id"] # Update the current ID

                # Update the state
                if self.data["sent"]:
                    self.sent = 1

                return OK

            except FileNotFoundError:
                logging.critical(f"invalid name {v} for local database")
                return ERROR

        except FileNotFoundError:
            logging.critical(f"directory {path} is non-existent")
            return ERROR   
        

    def merge_changes(self):
        """Merges the changes dict with the data dict (applies the pending changes)"""

        # create a temporary merged dict, check if it's consistent.
        # If it is, update self.data
        return OK

    def check_consistency(self, tmp_data):
        """Check if the data resulting from the changes are consistent:
           Prompt the inconsistency if they are not"""
        return OK

    
    def get_changes_from_last_sent(self):
        """Gets the changes between the last updated version (since you
        can't have called send() without first update()) and the last
        sent update (because this method is called from send(), so 
        these are the changes we need to notify: those we didn't notify
        before (those from the last time we notified)"""
        pass


    def get_payload(self):
        """Returns the dict to store in the file"""

        id, error = self.get_time()
        if error:
            return None, ERROR

        error = self.merge_changes()
        if error:
            return None, ERROR

        # id
        # sent (self.sent)
        # author (self.user)
        # teachers    [alphabetically ordered]
        # classes (?) [alphabetically ordered]
        # ddi         [alphabetically ordered]

        return {}, OK

    def update(self):
        """Updates the local database history"""

        try:
            pl, error = self.get_payload()
            if error:
                return ERROR

            with open(self.path + id + ".json", "w") as file:
                file.write(dumps(pl))
            
            print(f"Updated to version {self.id}\n")
            self.just_updated()

            return OK

        except FileNotFoundError:
            logging.critical(f"invalid name {v} for local database")
            return ERROR

    
    def send(self):
        """Sends the emails"""

        # BODY
        
        self.just_sent()
        self.update()
        self.push()
    

    def push(self):
        """Pushes the local database history to the drive"""

        # BODY

        self.just_pushed()


    def pull(self):
        """Pulls the database history from the drive"""

        # BODY

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


    def check_state(self, s: int):
        """Check if you can perform the action s on the basis of the states"""

        if not self.pulled:
            logger.warning(f"you have to {blue('pull')} first")
            return True, OK

        elif s == "pull":
            # You can always pull
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
                logger.warning(f"you have to {blue('update')} first")
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
                    logger.warning(f"you have to {blue('update')} first")
                    return True, OK
            else:
                logger.warning(f"you have to {blue('pull')} first")
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