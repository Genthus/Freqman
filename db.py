import sqlite3
from zipfile import ZipFile
import os
import shutil
import json
from .preferences import getPrefs
from .config import config

userDB = None
dictDB = None

userDBCursor = None
dictDBCursor = None

dbIsAttached = False

def dbInit():
    if not os.path.isdir(config('dbPath')):
        os.mkdir(config('dbPath'))
    global dbIsAttached
    dbIsAttached = False
    getUserDBCon()
    getDictDBCon()
    getUserDB()
    getDictDB()

def dbClose():
    closeUserDB()
    closeDictDB()

def closeUserDB():
    global userDB, userDBCursor
    if userDBCursor != None:
        userDBCursor.close()
        userDBCursor = None
    if userDB != None:
        userDB.close()
        userDB = None

def closeDictDB():
    global dictDB, dictDBCursor
    if dictDBCursor != None:
        dictDBCursor.close()
        dictDBCursor = None
    if dictDB != None:
        dictDB.close()
        dictDB = None


def getUserDB():
    global userDBCursor
    if userDBCursor == None:
        return getUserDBCon().cursor()
    userDBCursor.close()
    userDBCursor = getUserDBCon().cursor()
    return userDBCursor

def getUserDBCon():
    global userDB
    if userDB == None:
        userDB = sqlite3.connect(config('userDB'))
        verifyUserDatabase()
    return userDB

def getDictDB():
    global dictDBCursor
    if dictDBCursor == None:
        return getDictDBCon().cursor()
    dictDBCursor.close()
    dictDBCursor = getDictDBCon().cursor()
    return dictDBCursor

def getDictDBCon():
    global dictDB
    if dictDB == None:
        dictDB = sqlite3.connect(config('dictDB'))
        verifyDictDatabase()
    return dictDB

def dbAttached():
    global dbIsAttached
    if dbIsAttached:
        return dbIsAttached
    dbIsAttached = True
    return False

def createUserDatabase():
    schema = """
    CREATE TABLE IF NOT EXISTS cards(
        card INTEGER UNIQUE,
        term TEXT
    )
    """
    getUserDB().execute(schema)
    schema = """
    CREATE TABLE IF NOT EXISTS known(
        term TEXT UNIQUE
    )
    """
    getUserDB().execute(schema)
    schema = """
    CREATE TABLE IF NOT EXISTS sorted(
        card INTEGER,
        dict TEXT
    )
    """
    getUserDB().execute(schema)
    schema = """
    CREATE TABLE IF NOT EXISTS updated(
        card INTEGER UNIQUE
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
        name TEXT UNIQUE
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

def rmDictFromDB(name):
    if name == "None":
        return
    # TODO completely remove dicts table, its unnecessary and might cause errors
    getDictDB().execute("""
    DELETE FROM dicts
    WHERE name = ?
    """,(name,))
    getDictDBCon().commit()
    getDictDB().execute("""
    DELETE FROM terms
    WHERE dict = ?
    """,(name,))
    getDictDBCon().commit()

def getDicts():
    res = getDictDB().execute("SELECT name FROM dicts")
    return res.fetchall() 

def addCardsToUserDB(cards):
    getUserDB().executemany("INSERT INTO cards VALUES (?,?)",cards)
    getUserDBCon().commit()

def addSortedCards(cards):
    # TODO this is bad
    clearSortedCards()
    getUserDB().executemany("INSERT INTO sorted VALUES (?,?)",cards)
    getUserDBCon().commit()

def clearSortedCards():
    getUserDB().execute("DELETE FROM sorted")
    getUserDBCon().commit()

def addKnownCards(cards):
    # TODO this looks very inneficcient
    getUserDB().execute("DELETE FROM known")
    getUserDBCon().commit()
    getUserDB().execute("""
    INSERT INTO known 
        SELECT term
        FROM cards
        WHERE card IN (?)
    """,(','.join(cards),))
    getUserDBCon().commit()

def getKnownCards():
    res = getUserDB().execute("SELECT term FROM known")
    return res.fetchall()

def addCardToUpdate(c):
    for cardType in getPrefs()['filter']:
        if c.type == cardType['type']:
            getUserDB().execute("INSERT INTO updated VALUES (?)",(c,))
    getUserDBCon().commit()

def getUpdatedCards():
    res = getUserDB().execute("SELECT card FROM updated")
    return res.fetchall()

def getTermInDictDB(s) -> tuple:
    dictName = getPrefs()['setDict']
    if dictName == "None":
        return ()
    res = getDictDB().execute("SELECT term, value FROM terms WHERE term='?' AND dict = '?'",(s,dictName))
    if res.fetchone() == None:
        return ()
    return res.fetchone()

def getCardsWithFreq():
    if not dbAttached():
        getUserDB().execute("ATTACH DATABASE ? AS source",(config('dictDB'),))
    res = getUserDB().execute("""
    SELECT card, freq
    FROM cards 
    INNER JOIN source.terms
    ON cards.term = source.terms.term
    WHERE dict = ?
    AND card NOT IN (SELECT card FROM sorted WHERE dict != ?)
    """,(getPrefs()['setDict'],getPrefs()['setDict']))
    return res.fetchall()
    
def resetUserDB():
    getUserDB().execute("DELETE FROM cards")
    getUserDBCon().commit()
    getUserDB().execute("DELETE FROM known")
    getUserDBCon().commit()
    getUserDB().execute("DELETE FROM sorted")
    getUserDBCon().commit()
    getUserDB().execute("DELETE FROM updated")
    getUserDBCon().commit()
    createUserDatabase()
    getUserDBCon().commit()
