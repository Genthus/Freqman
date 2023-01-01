import sqlite3
from zipfile import ZipFile
import os
import shutil
import json
from .preferences import getPrefs
from .config import config

userDB = None
dictDB = None

def dbInit():
    if not os.path.isdir(config('dbPath')):
        os.mkdir(config('dbPath'))
    getUserDB()
    getDictDB()

def dbClose():
    if userDB != None:
        userDB.close()
    if dictDB != None:
        dictDB.close()

def getUserDB():
    return getUserDBCon().cursor()

def getUserDBCon():
    global userDB
    if userDB == None:
        userDB = sqlite3.connect(config('userDB'))
        verifyUserDatabase()
    return userDB

def getDictDB():
    return getDictDBCon().cursor()

def getDictDBCon():
    global dictDB
    if dictDB == None:
        dictDB = sqlite3.connect(config('dictDB'))
        verifyDictDatabase()
    return dictDB

def createUserDatabase():
    schema = """
    CREATE TABLE IF NOT EXISTS known(
        term TEXT
    )
    """
    getUserDB().execute(schema)

def verifyUserDatabase():
    try:
        tables = getUserDB().execute("SELECT tbl_name FROM sqlite_master WHERE type='table'")
    except sqlite3.OperationalError:
        createUserDatabase()
        return
    if 'known' not in tables.fetchall():
        createUserDatabase()
    return True

def createDictDatabase():
    schema = """
    CREATE TABLE IF NOT EXISTS terms(
        term TEXT,
        freq INTEGER,
        dict TEXT
    )
    """
    getDictDB().execute(schema)
    schema = """
    CREATE TABLE IF NOT EXISTS dicts(
        name TEXT
    )
    """
    getDictDB().execute(schema)

def verifyDictDatabase():
    try:
        tables = getDictDB().execute("SELECT tbl_name FROM sqlite_master WHERE type='table'")
    except sqlite3.OperationalError:
        createDictDatabase()
        return
    if 'dicts' not in tables.fetchall():
        createDictDatabase()
    return True

def importYomichanFreqDict(path):
    with ZipFile(path) as zip:
        zip.extractall(path="./temp")
    dictData = {}
    with open(os.path.join("./temp","index.json")) as f:
        data = json.load(f)
        dictData['title'] = data['title']
        if dictData['title'] == 'None':
            # exception for None name
            return "Name cannot be None"
    tableInDB = getDictDB().execute("SELECT name FROM dicts")
    if dictData['title'] in tableInDB.fetchall():
        return "table already in DB"
    getDictDB().execute("INSERT INTO dicts VALUES (?)", (dictData['title'],))
    termcount = 0
    for file in os.listdir("./temp"):
        terms = []
        if "term_meta_bank" in file:
            with open(os.path.join("./temp",file)) as f:
                terms = json.load(f)
            # very rough verification of the dictionary
            if len(terms) <= 0:
                return "got no terms"
            if len(terms[0]) != 3:
                return f"dictionary format error, has %d terms"%len(terms[0])
            if terms[0][1] != "freq":
                return "dictionary format error, second value isnt freq"

            newTerms = []
            if type(terms[0][2]) == int:
                for t in terms:
                    newTerms.append([t[0],t[2],dictData['title']])
            elif type(terms[0][2]) == dict:
                for t in terms:
                    newTerms.append([t[0],t[2]['frequency'],dictData['title']])
            getDictDB().executemany("INSERT INTO terms VALUES (?,?,?)",newTerms)
            termcount += len(terms)
            

    shutil.rmtree("./temp")
    getDictDBCon().commit()
    return "Success, added " + str(termcount) + " terms"

def getDicts():
    res = getDictDB().execute("SELECT name FROM dicts")
    return res.fetchall() 

def addTermToUserDB(s):
    getUserDB().execute("INSERT INTO known VALUES (?)",(s,))

def getTermInDictDB(s) -> tuple:
    dictName = getPrefs()['setDict']
    if dictName == "None":
        return ()
    res = getDictDB().execute("SELECT term, value FROM terms WHERE term='?' AND dict = '?'",(s,dictName))
    if res.fetchone() == None:
        return ()
    return res.fetchone()
    
def checkIfTermInUserDB(s) -> bool:
    res = getUserDB().execute("SELECT term FROM known WHERE term='?'",s)
    if res.fetchone() == None:
        return False
    return True 
