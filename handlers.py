import logging
from json import dumps, loads
import pandas as pd
from datetime import datetime
import os

DATABASE      = "database\\"
EXCEL_DOCENTI = r"dati\docenti.xlsx"
EXCEL_CLASSI  = r"dati\classi.xlsx"
STUDENTI_DDI  = r"studenti_DDI.xlsx"


def update(args, opts):
    if "-h" in opts or "--help" in opts:
        message  = "update the local database:"
        message += "\nuse this command after any change to the local excel files" 
        print(message)
        return

    error, version = excel_to_json()
    if  error:
        return

    print(f"Updated to version {version}\n")


def push(args, opts):
    if "-h" in opts or "--help" in opts:
        message  = "push the local changes to the remote database:"
        message += "\nuse this command after any local change" 
        print(message)
        return

    print("Push")
    print(args)
    print(opts)


def pull(args, opts):
    if "-h" in opts or "--help" in opts:
        message  = "update the local data using the remote ones:"
        message += "\nuse this command before making any change to the local excel files" 
        print(message)
        return

    print("Pull")
    print(args)
    print(opts)


def send(args, opts):
    if "-h" in opts or "--help" in opts:
        message  = "notify the teachers about the changes in their classrooms:"
        message += "\nuse this command after 'update' and before 'push'" 
        print(message)
        return

    print("Send")
    print(args)
    print(opts)


def status(args, opts):
    if "-h" in opts or "--help" in opts:
        message  = "get an overview of the current DDI status:"
        message += "\nuse this command to get all the insights about the data" 
        print(message)
        return

    print("Status")
    print(args)
    print(opts)


def check(args=[], opts=[]):
    if "-h" in opts or "--help" in opts:
        message  = "check if the names and classrooms match:"
        message += "\nuse this before anything else"
        print(message)
        return
    
    ddi     = pd.read_excel(STUDENTI_DDI)
    classi  = pd.read_excel(EXCEL_CLASSI)
    docenti = pd.read_excel(EXCEL_DOCENTI)

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
    if "-h" in opts or "--help" in opts:
        message  = "restores the version corresponding to the last local database:"
        message += "\nuse this to discard unwanted changes"
        print(message)
        return

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


def excel_to_json():
    if check():
        return 1, 1

    id = get_time()

    docenti = pd.read_excel(EXCEL_DOCENTI, keep_default_na=False)
    classi  = pd.read_excel(EXCEL_CLASSI, keep_default_na=False)
    ddi     = pd.read_excel(STUDENTI_DDI, keep_default_na=False)

    database = {"id": id, "docenti": docenti.to_dict('list'), "classi": classi.to_dict('list'), "ddi": ddi.to_dict('list')}
    
    with open(DATABASE + id + ".json", "w") as file:
        file.write(dumps(database))
    
    return 0, id


def json_to_excel(version):
    try:
        with open(DATABASE + version + ".json", "r") as file:
            database = loads(file.read())
        
        docenti = pd.DataFrame(database["docenti"])
        classi  = pd.DataFrame(database["classi"])
        ddi     = pd.DataFrame(database["ddi"])

        docenti.to_excel(EXCEL_DOCENTI, index=False)
        classi.to_excel(EXCEL_CLASSI, index=False)
        ddi.to_excel(STUDENTI_DDI, index=False)
        
    except PermissionError:
        print("ERROR - cannot write to excel (check if the program is running and close it)")