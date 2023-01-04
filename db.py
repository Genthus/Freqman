import sqlite3
from zipfile import ZipFile
import os
import shutil
import json
import tempfile
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
        term TEXT UNIQUE,
        card INTEGER NOT NULL,
        FOREIGN KEY (card)
            REFERENCES cards (card)
            ON UPDATE CASCADE
            ON DELETE CASCADE
    )
    """
    getUserDB().execute(schema)
    schema = """
    CREATE TABLE IF NOT EXISTS sorted(
        card INTEGER,
        dict TEXT,
        FOREIGN KEY (card)
            REFERENCES cards (card)
            ON UPDATE CASCADE
            ON DELETE CASCADE
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

def verifyDictDatabase():
    try:
        tables = getDictDB().execute("SELECT tbl_name FROM sqlite_master WHERE type='table'")
    except sqlite3.OperationalError:
        createDictDatabase()
        return
    return True

def importYomichanFreqDict(path):
    tempFolder = os.path.join(tempfile.gettempdir(),'freqManYomiImport')
    try:
        shutil.rmtree(tempFolder)
    except FileNotFoundError:
        # temp folder file existed
        print("")
    os.mkdir(tempFolder)

    with ZipFile(path) as zip:
        zip.extractall(tempFolder)
    dictData = {}
    with open(os.path.join(tempFolder,"index.json")) as f:
        data = json.load(f)
        dictData['title'] = data['title']
        if dictData['title'] == 'None':
            # exception for None name
            return "Name cannot be None"
    tableInDB = getDictDB().execute("SELECT dict FROM terms GROUP BY dict")
    if dictData['title'] in tableInDB.fetchall():
        return "table already in DB"
    termcount = 0
    for file in os.listdir(tempFolder):
        terms = []
        if "term_meta_bank" in file:
            with open(os.path.join(tempFolder,file)) as f:
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
                termName = 'frequency'
                try:
                    print(terms[0][2][termName])
                except KeyError:
                    termName = 'value'
                for t in terms:
                    try:
                        newTerms.append([t[0],t[2][termName],dictData['title']])
                    except KeyError:
                        # JPDB schema issue
                        try:
                            newTerms.append([t[0],t[2]['frequency'][termName],dictData['title']])
                        except KeyError:
                            print(t)
            getDictDB().executemany("INSERT INTO terms VALUES (?,?,?)",newTerms)
            termcount += len(terms)
            
    shutil.rmtree(tempFolder)
    getDictDBCon().commit()
    return "Success, added " + str(termcount) + " terms"

def rmDictFromDB(name):
    if name == "None":
        return
    getDictDBCon().commit()
    getDictDB().execute("""
    DELETE FROM terms
    WHERE dict = ?
    """,(name,))
    getDictDBCon().commit()

def getDicts():
    res = getDictDB().execute("SELECT dict FROM terms GROUP BY dict")
    return res.fetchall() 

def addCardsToUserDB(cards):
    getUserDB().executemany("INSERT INTO cards VALUES (?,?)",cards)
    getUserDBCon().commit()

def addSortedCards(cards):
    getUserDB().executemany("INSERT INTO sorted VALUES (?,?)",cards)
    getUserDBCon().commit()

def clearSortedCards():
    getUserDB().execute("DELETE FROM sorted")
    getUserDBCon().commit()

def addKnownCards(cards):
    # TODO this looks very inneficcient
    getUserDB().execute("DELETE FROM known")
    getUserDBCon().commit()
    getUserDB().executemany("""
    INSERT INTO known (term,card)
        SELECT term, card
        FROM cards
        WHERE card IN (?)
    """,[(c,) for c in cards])
    getUserDBCon().commit()

def getCardsWithKnownTerms():
    res = getUserDB().execute("""
    SELECT card
    FROM cards
    WHERE term IN (SELECT term FROM known)
    AND card NOT IN (SELECT card FROM known)
    """)
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
    AND card NOT IN (SELECT card FROM known)
    AND card NOT IN (SELECT card FROM sorted)
    """,(getPrefs()['setDict'],))
    return res.fetchall()

def getCardsWithoutFreq():
    if not dbAttached():
        getUserDB().execute("ATTACH DATABASE ? AS source",(config('dictDB'),))
    res = getUserDB().execute("""
    SELECT card
    FROM cards 
    WHERE card NOT IN (
        SELECT card
        FROM cards
        LEFT JOIN source.terms
        ON cards.term = source.terms.term
        WHERE dict = ?
    )
    AND card NOT IN (SELECT card FROM known)
    AND card NOT IN (SELECT card FROM sorted)
    """,(getPrefs()['setDict'],))
    return res.fetchall()

def getHighestFreqVal():
    res = getDictDB().execute("SELECT freq FROM terms ORDER BY freq DESC LIMIT 1")
    return res.fetchone()

def removeCardFromUserDB(id):
    getUserDB().execute("DELETE FROM cards WHERE card=?",(id,))
    getUserDBCon().commit()

    
def resetUserDB():
    getUserDB().execute("DELETE FROM cards")
    getUserDB().execute("DROP TABLE cards")
    getUserDBCon().commit()
    getUserDB().execute("DELETE FROM known")
    getUserDB().execute("DROP TABLE known")
    getUserDBCon().commit()
    getUserDB().execute("DELETE FROM sorted")
    getUserDB().execute("DROP TABLE sorted")
    getUserDBCon().commit()
    createUserDatabase()
    getUserDBCon().commit()
