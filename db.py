import sqlite3
from zipfile import ZipFile
import os
import shutil
import json
from . import preferences as prefs

userDB = None
dictDB = None

def getUserDB():
    global userDB
    if userDB == None:
        userDB = sqlite3.connect("./user_data/user.db")
        verifyUserDatabase()
    return userDB


def getDictDB():
    global dictDB
    if dictDB == None:
        dictDB = sqlite3.connect("./user_data/dict.db")
        verifyDictionaryDatabase()
    return dictDB

def createUserDatabase():
    schema = """
    CREATE TABLE known(
        term TEXT
    )
    """
    getUserDB().cursor().execute(schema)

def verifyUserDatabase():
    tables = getUserDB().execute("SELECT tableName FROM sqlite_master WHERE type='table'").fetchall()
    if 'known' not in tables:
        print("Error in userDB")
        return False
    elif tables is ():
        # TODO add error check here
        createUserDatabase()
    return True

def createDictDatabase():
    schema = """
    CREATE TABLE dicts(
        name TEXT
    )
    """
    getDictDB().cursor().execute(schema)

def importYomichanFreqDict(path):
    with ZipFile(path,'r') as zip:
        zip.extractall(path="./temp")
    dictData = {}
    with open(os.path.join("./temp","index.json")) as f:
        data = json.load(f)
        dictData['title'] = data['title']
    tableInDB = getDictDB().execute("SELECT tableName FROM sqlite_master WHERE type='table' AND tableName='?'",dictData['title'])
    if tableInDB.fetchall() is not None:
        print("table already in DB")
        # throw error
        return False
    getDictDB().execute("""
    INSERT INTO dicts VALUES (?)
    """, dictData['title'])
    getDictDB().execute("""
    CREATE TABLE ?(
        term TEXT,
        freq INTEGER
    """,dictData['title'])
    terms = []
    for file in os.listdir("./temp"):
        if "term_meta_bank" in file:
            with open(os.path.join("./temp",file)) as f:
                data = json.load(f)
                terms.append(data)
    # very rough verification of the dictionary
    if len(terms[0]) != 3:
        return False
    if terms[0][1] != "freq":
        return False
    if type(terms[0][2]) is int:
        getDictDB().executemany("INSERT INTO ? VALUES (?,?)",(dictData['title'],terms[0],terms[2]))
    elif type(terms[0][2]) is dict:
        getDictDB().executemany("INSERT INTO ? VALUES (?,?)",(dictData['title'],terms[0],terms[2]['frequency']))

    shutil.rmtree("./temp")
    return True

def verifyDictionaryDatabase():
    tables = getDictDB().execute("SELECT tableName FROM sqlite_master WHERE type='table'").fetchall()
    if 'dicts' not in tables:
        print("Error in DictDB")
        return False
    elif tables is ():
        # TODO add an error check here
        createDictDatabase()
    return True

def addTermToUserDB(s):
    getUserDB.execute("INSERT INTO known VALUES (?)",s)

def getTermInDictDB(s) -> tuple:
    res = getDictDB().execute("SELECT term, value FROM ? WHERE term='?'",(prefs.getJsonConfig()['setDict'],s))
    if res.fetchone() is None:
        return ()
    return res.fetchone()
    
def checkIfTermInUserDB(s) -> bool:
    res = getUserDB().execute("SELECT term FROM known WHERE term='?'",s)
    if res.fetchone() is None:
        return False
    return True 
