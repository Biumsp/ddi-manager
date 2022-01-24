import logging
from json import dumps, loads
import pandas as pd
from datetime import datetime
import os
from functions import *

DATABASE      = "database\\"
EXCEL_DOCENTI = r"dati\docenti.xlsx"
EXCEL_CLASSI  = r"dati\classi.xlsx"
STUDENTI_DDI  = r"studenti_DDI.xlsx"

STATE_TO_PULL   = 1
STATE_TO_UPDATE = 2
STATE_TO_SEND   = 3
STATE_TO_PUSH   = 4

def update(args, opts):

    # Help --------------------------------------------------------------------
    if "-h" in opts or "--help" in opts:
        message  = "update the local database:"
        message += "\nuse this command after any change to the local excel files" 
        print(message)
        return
    # -------------------------------------------------------------------------

    error, diff = find_diff(from_excel=True)
    if error:
        return

    if diff:
        error, database = excel_to_dict()
        if  error:
            return
        
        with open(DATABASE + database["id"] + ".json", "w") as file:
            file.write(dumps(database))

        print(f"Updated to version {database['id']}\n")
    else:
        print("Nothing to update\n")



def push(args, opts):

    # Help --------------------------------------------------------------------
    if "-h" in opts or "--help" in opts:
        message  = "push the local changes to the remote database:"
        message += "\nuse this command after any local change" 
        print(message)
        return
    # -------------------------------------------------------------------------

    print("Push")
    print(args)
    print(opts)



def pull(args, opts):

    # Help --------------------------------------------------------------------
    if "-h" in opts or "--help" in opts:
        message  = "update the local data using the remote ones:"
        message += "\nuse this command before making any change to the local excel files" 
        print(message)
        return
    # -------------------------------------------------------------------------

    print("Pull")
    print(args)
    print(opts)



def send(args, opts):

    # Help --------------------------------------------------------------------
    if "-h" in opts or "--help" in opts:
        message  = "notify the teachers about the changes in their classrooms:"
        message += "\nuse this command after 'update' and before 'push'" 
        print(message)
        return
    # -------------------------------------------------------------------------

    error, v = get_last_version()

    if error:
        return
    id = v["id"]

    FORCE = ("-f" in opts or "--force" in opts)
    if v["last_sent"] == id and not FORCE:
        print(f"The teachers were already notified at time {v['last_sent']}\n")
        return
    elif v["last_sent"] == id and FORCE:
        print("Forcing to send the updates again\n")
        error, diff = find_diff(ignore_first=True)
    else:
        error, diff = find_diff()
    
    if not diff:
        print("Nothing changed from the last version\n")
        return

    teachers = teachers_from_diff(diff)
    error = send_emails(teachers, diff)
    if error:
        return

    #change_state(SENT)

    v["last_sent"] = id

    with open(DATABASE + id + ".json", "w") as file:
        file.write(dumps(v))

    print("Sent email to:\n")
    for t, c in teachers.items():
        print(f"- {t:25} -- {''.join(c)}")

    print()



def status(args, opts):

    # Help --------------------------------------------------------------------
    if "-h" in opts or "--help" in opts:
        message  = "get an overview of the current DDI status:"
        message += "\nuse this command to get all the insights about the data" 
        print(message)
        return
    # -------------------------------------------------------------------------

    v: dict = get_last_version()

    ddi = v["ddi"]
    ddi_dict = clean_dict(ddi)
    
    print(f"Ci sono {sum(len(v) for v in ddi_dict.values())} studenti in DDI")
    print(f"Le classi con studenti a casa sono {len(ddi_dict)}")

    if "-d" in opts or "--detailed" in opts:
        print()
        for c, v in ddi_dict.items():
            print(f"classe {c:8} - {len(v)} studenti")
    


def check(args=[], opts=[]):

    # Help --------------------------------------------------------------------
    if "-h" in opts or "--help" in opts:
        message  = "check if the names and classrooms match:"
        message += "\nuse this before anything else"
        print(message)
        return
    # -------------------------------------------------------------------------
    
    ddi     = pd.read_excel(STUDENTI_DDI)
    classi  = pd.read_excel(EXCEL_CLASSI)
    docenti = pd.read_excel(EXCEL_DOCENTI)

    # Check if the classes in STUDENTI_DDI exist in EXCEL_CLASSI -------------- 
    invalid = []
    for c in ddi.columns:
        if c not in classi.columns:
            invalid.append(c)
    
    if invalid:
        print(f"ERROR - le classi in {STUDENTI_DDI} non corrispondono a quelle in {EXCEL_CLASSI}")
        for c in invalid:
            print(f"Invalid class: {c}")

    return invalid



def restore(args, opts):

    # Help --------------------------------------------------------------------
    if "-h" in opts or "--help" in opts:
        message  = "restores the version corresponding to the last local database:"
        message += "\nuse this to discard unwanted changes"
        print(message)
        return
    # -------------------------------------------------------------------------

    versions = os.listdir(DATABASE)
    versions = [x.split(".")[0] for x in versions]
    if args:
        if args[0] not in versions:
            print(f"ERROR - invalid version {args[0]}\n")
            return
        else:
            json_to_excel(args[0])

    else:
        v = str(max([int(x) for x in versions]))
        json_to_excel(v)



# Auxiliary functions ----------------------------------------------------
# ========================================================================

def get_state():
    try:
        with open("state", "r") as file:
            try:
                state = int(file.read())
            except ValueError:
                logging.critical("corrupted state")
                return 1, 0

        return 0, int(state)

    except FileNotFoundError:
        logging.critical("state not found")
        return 1, 0

def send_emails(teachers, diff):
    pass


def change_state(n):
    try:
        with open("state", "w") as file:
            file.write(str(n))
    except:
        logging.critical("unable to change state")
        return 1


def find_diff(from_excel=False, ignore_first=False):
    if from_excel:
        error, lastv = excel_to_dict()
        if error:
            return 1, {}
    else:
        error, lastv = get_last_version()
    
    if ignore_first:
        prevv: dict = get_version(get_version(lastv["previous"])["last_sent"])
    else:
        prevv: dict = get_version(lastv["last_sent"])
    
    lastddi  = lastv["ddi"]
    prevddi  = prevv["ddi"]

    diff = {}
    for c in set(list(lastddi.keys()) + list(prevddi.keys())):
        if c in lastddi and c in prevddi:
            if set(lastddi[c]) != set(prevddi[c]):
                print(set(lastddi[c]), set(prevddi[c]))
                diff.update({c: {"old": prevddi[c], "new": lastddi[c]}})

        elif c in lastddi:
            diff.update({c: {"old": [], "new": lastddi[c]}})

        else:
            diff.update({c: {"old": prevddi[c], "new": []}})
    
    return 0, diff


def clean_dict(waste: dict): # NONVA
    sweet = {}
    for k in waste.keys():
        waste[k] = [x for x in waste[k] if x != ""]

        if waste[k]:
            sweet.update({k: waste[k]})

    return sweet


def get_version(v):
    with open(DATABASE + v + ".json", "r") as file:
            version = loads(file.read())
    return version


def get_last_version():
    v = str(max([int(x.split(".")[0]) for x in os.listdir(DATABASE)]))
    with open(DATABASE + v + ".json", "r") as file:
        v = loads(file.read()) 
    return 0, v  


def get_time():
    now = datetime.now()

    year  = str(now.year)
    month = str(now.month)
    day   = str(now.day)
    hour  = str(now.hour)
    minute = str(now.minute)
    second = str(now.second)

    month  = "0"*(2-len(month))  + month
    day    = "0"*(2-len(day))    + day
    hour   = "0"*(2-len(hour))   + hour
    minute = "0"*(2-len(minute)) + minute
    second = "0"*(2-len(second)) + second

    return  year + month + day + hour + minute + second


def get_last_sent():
    versions = os.listdir(DATABASE)
    versions = [x.split('.')[0] for x in versions]
    versions.sort(key=lambda x: int(x), reverse=True)

    for v in versions:
        v = get_version(v)
        if v["id"] == v["last_sent"]:
            return 0, v["id"]
    
    logging.error("no previous version was ever sent")
    return 1, 0



def excel_to_dict():
    if check():
        return 1, {}

    id = get_time()

    docenti = pd.read_excel(EXCEL_DOCENTI, keep_default_na=False)
    classi  = pd.read_excel(EXCEL_CLASSI,  keep_default_na=False)
    ddi     = pd.read_excel(STUDENTI_DDI,  keep_default_na=False)

    ddi = clean_dict(ddi.to_dict('list'))
    
    error, lastsent = get_last_sent()
    if error:
        return 1, {}
    
    error, previous = get_last_version()
    if error:
        return 1, {}

    database = {"id": id, "last_sent": lastsent, "previous": previous,
                "docenti": docenti.to_dict('list'), 
                "classi": classi.to_dict('list'), "ddi": ddi}
    
    return 0, database


def json_to_excel(version):
    try:
        database = get_version(version)
        
        docenti = pd.DataFrame({k: pd.Series(v) for k,v in database["docenti"].items()}).dropna()
        classi  = pd.DataFrame({k: pd.Series(v) for k,v in database["classi"].items()}).dropna()
        ddi     = pd.DataFrame({k: pd.Series(v) for k,v in database["ddi"].items()}).dropna()

        docenti.to_excel(EXCEL_DOCENTI, index=False)
        classi.to_excel(EXCEL_CLASSI, index=False)
        ddi.to_excel(STUDENTI_DDI, index=False)
        
    except PermissionError:
        print("ERROR - cannot write to excel (check if the program is running and close it)")


def teachers_from_diff(diff):
    classi  = pd.read_excel(EXCEL_CLASSI,  keep_default_na=False)

    teachers = {}
    for c in diff.keys():
        for t in classi[c]:
            if t not in teachers:
                teachers.update({t: []})
            
            teachers[t].append(c)

    return teachers