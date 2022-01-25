from logging_setup import logger, log_level_info


def pull(args, opts, database):

    # Help --------------------------------------------------------------------
    if "-h" in opts or "--help" in opts:
        message  = "update the local data using the remote ones:"
        message += "\nuse this command before making any change to the local excel files" 
        print(message)
        return
    # -------------------------------------------------------------------------

    # Change Log Level to info ------------------------------------------------
    if "-i" in opts or "--info" in opts:
        logger.setLevel(log_level_info)
    # -------------------------------------------------------------------------

    # Check if the state is correct -------------------------------------------
    stop = database.check_state("pull")
    if stop:
        return
    # -------------------------------------------------------------------------

    database.pull()


def update(args, opts, database):

    # Help --------------------------------------------------------------------
    if "-h" in opts or "--help" in opts:
        message  = "update the local database:"
        message += "\nuse this command after any change to the local excel files" 
        print(message)
        return
    # -------------------------------------------------------------------------

    # Change Log Level to info ------------------------------------------------
    if "-i" in opts or "--info" in opts:
        logger.setLevel(log_level_info)
    # -------------------------------------------------------------------------

    # Check if the state is correct -------------------------------------------
    stop, error = database.check_state("pull")
    if stop or error:
        return
    # -------------------------------------------------------------------------

    # Update ------------------------------------------------------------------

    database.update()


def push(args, opts, database):

    # Help --------------------------------------------------------------------
    if "-h" in opts or "--help" in opts:
        message  = "push the local changes to the remote database:"
        message += "\nuse this command after any local change" 
        print(message)
        return
    # -------------------------------------------------------------------------

    # Change Log Level to info ------------------------------------------------
    if "-i" in opts or "--info" in opts:
        logger.setLevel(log_level_info)
    # -------------------------------------------------------------------------

    # Check if the state is correct -------------------------------------------
    stop, error = database.check_state("push")
    if stop or error:
        return
    # -------------------------------------------------------------------------

    database.push()


def send(args, opts, database):

    # Help --------------------------------------------------------------------
    if "-h" in opts or "--help" in opts:
        message  = "notify the teachers about the changes in their classrooms:"
        message += "\nuse this command after 'update' and before 'push'" 
        print(message)
        return
    # -------------------------------------------------------------------------

    # Change Log Level to info ------------------------------------------------
    if "-i" in opts or "--info" in opts:
        logger.setLevel(log_level_info)
    # -------------------------------------------------------------------------

    # Check if the state is correct -------------------------------------------
    stop, error = database.check_state("send")
    if stop or error:
        return
    # -------------------------------------------------------------------------

    database.send()



def status(args, opts, database):

    # Help --------------------------------------------------------------------
    if "-h" in opts or "--help" in opts:
        message  = "get an overview of the current DDI status:"
        message += "\nuse this command to get all the insights about the data" 
        print(message)
        return
    # -------------------------------------------------------------------------

    # Change Log Level to info ------------------------------------------------
    if "-i" in opts or "--info" in opts:
        logger.setLevel(log_level_info)
    # -------------------------------------------------------------------------

    ddi = database.data["ddi"]

    message  = f"Ci sono {sum(len(v) for v in ddi.values())} studenti in DDI\n"
    message += f"Le classi con studenti a casa sono {len(ddi)}\n"

    if ("-d" in opts or "--detailed" in opts):
        message += "\n"
        for c, v in ddi_dict.items():
            message += f"+ {c:8} - {len(v)} studenti ==> {'; '.join(v)}\n")

    if ("-f" in opts or "--file" in opts):
        with open("status.txt", "w") as file:
            file.write(message)
    else:
        print(message)



def restore(args, opts, database):

    # Help --------------------------------------------------------------------
    if "-h" in opts or "--help" in opts:
        message  = "restores the version corresponding to the last local database:"
        message += "\nuse this to discard unwanted changes"
        print(message)
        return
    # -------------------------------------------------------------------------

    # Change Log Level to info ------------------------------------------------
    if "-i" in opts or "--info" in opts:
        logger.setLevel(log_level_info)
    # -------------------------------------------------------------------------

    # Check if the state is correct -------------------------------------------
    stop, error = database.check_state("restore")
    if stop or error:
        return
    # -------------------------------------------------------------------------

    database.restore()




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
