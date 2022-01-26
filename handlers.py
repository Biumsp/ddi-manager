from logging_setup import logger, log_level_info


def pull(args, opts, database):

    # Help --------------------------------------------------------------------
    if "-h" in opts or "--help" in opts:
        message  = "update the local database using the remote one:"
        message += "\nuse this command before sending the updates to the teachers" 
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

    database.pull()


def update(args, opts, database):

    # Help --------------------------------------------------------------------
    if "-h" in opts or "--help" in opts:
        message  = "save the modified version and add it to the local database:"
        message += "\nuse this command after any change" 
        print(message)
        return
    # -------------------------------------------------------------------------

    # Change Log Level to info ------------------------------------------------
    if "-i" in opts or "--info" in opts:
        logger.setLevel(log_level_info)
    # -------------------------------------------------------------------------

    # Check if the state is correct -------------------------------------------
    stop, error = database.check_state("update")
    if stop or error:
        return
    # -------------------------------------------------------------------------

    # Update ------------------------------------------------------------------

    database.update()


def push(args, opts, database):

    # Help --------------------------------------------------------------------
    if "-h" in opts or "--help" in opts:
        message  = "push the local changes to the remote database:"
        message += "\nuse this command after a local update" 
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
        message += "\nuse this command after update or push}" 
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
        message += "\nuse this command to get some insights about the data" 
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
            message += f"+ {c:8} - {len(v)} studenti ==> {'; '.join(v)}\n"

    if ("-f" in opts or "--file" in opts):
        with open("status.txt", "w") as file:
            file.write(message)
    else:
        print(message)



def restore(args, opts, database):

    # Help --------------------------------------------------------------------
    if "-h" in opts or "--help" in opts:
        message  = "restores the last version present in the local database:"
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



def add(args, opts, database):

    # Help --------------------------------------------------------------------
    if "-h" in opts or "--help" in opts:
        message  = "add a student to the list of ddi students"
        print(message)
        return
    # -------------------------------------------------------------------------

    # Change Log Level to info ------------------------------------------------
    if "-i" in opts or "--info" in opts:
        logger.setLevel(log_level_info)
    # -------------------------------------------------------------------------

    # Check if the state is correct -------------------------------------------
    stop, error = database.check_state("add")
    if stop or error:
        return
    # -------------------------------------------------------------------------

    # TODO extract name and class from args

    #database.add((name, classe))
    database.add((args[0], args[1])) # Temporary


def remove(args, opts, database):

    # Help --------------------------------------------------------------------
    if "-h" in opts or "--help" in opts:
        message  = "remove a student from the list of ddi students"
        print(message)
        return
    # -------------------------------------------------------------------------

    # Change Log Level to info ------------------------------------------------
    if "-i" in opts or "--info" in opts:
        logger.setLevel(log_level_info)
    # -------------------------------------------------------------------------

    # Check if the state is correct -------------------------------------------
    stop, error = database.check_state("remove")
    if stop or error:
        return
    # -------------------------------------------------------------------------

    # TODO extract name and class from args

    #database.remove((name, classe))
    database.remove((args[0], args[1])) # Temporary


def list_class(args, opts, database):

    # Help --------------------------------------------------------------------
    if "-h" in opts or "--help" in opts:
        message  = "list the students and teachers of a class"
        print(message)
        return
    # -------------------------------------------------------------------------

    # Change Log Level to info ------------------------------------------------
    if "-i" in opts or "--info" in opts:
        logger.setLevel(log_level_info)
    # -------------------------------------------------------------------------

    # Check if the state is correct -------------------------------------------
    stop, error = database.check_state("list")
    if stop or error:
        return
    # -------------------------------------------------------------------------

    database.list_class(args[0])


def test(args, opts, database):
    pass

def get_state(args, opts, database):
    print(f"updated = {database.updated}")
    print(f"sent = {database.sent}")
    print(f"pulled = {database.pulled}")
    print(f"pushed = {database.pushed}")
    print(f"id = {database.id}")


# def clean_dict(waste: dict): # NONVA
#     sweet = {}
#     for k in waste.keys():
#         waste[k] = [x for x in waste[k] if x != ""]

#         if waste[k]:
#             sweet.update({k: waste[k]})

#     return sweet



# def json_to_excel(version):
#     try:
#         database = get_version(version)
        
#         docenti = pd.DataFrame({k: pd.Series(v) for k,v in database["docenti"].items()}).dropna()
#         classi  = pd.DataFrame({k: pd.Series(v) for k,v in database["classi"].items()}).dropna()
#         ddi     = pd.DataFrame({k: pd.Series(v) for k,v in database["ddi"].items()}).dropna()

#         docenti.to_excel(EXCEL_DOCENTI, index=False)
#         classi.to_excel(EXCEL_CLASSI, index=False)
#         ddi.to_excel(STUDENTI_DDI, index=False)
        
#     except PermissionError:
#         print("ERROR - cannot write to excel (check if the program is running and close it)")
