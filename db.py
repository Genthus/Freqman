import sqlite3
from zipfile import ZipFile
import os
import shutil
import json
import tempfile
from contextlib import closing
from .preferences import getPrefs
from .config import config

userDB = None
dictDB = None

def dbInit():
    if not os.path.isdir(config('dbPath')):
        os.mkdir(config('dbPath'))

def getDictDB():
    global dictDB
    if dictDB == None:
        dictDB = config('dictDB')
    return dictDB

def getUserDB():
    global userDB
    if userDB == None:
        userDB = config('userDB')
    return userDB

def createUserDatabase():
    with closing(sqlite3.connect(getUserDB())) as connection:
        with closing(connection.cursor()) as cursor:
            schema = """
            CREATE TABLE IF NOT EXISTS cards(
                card INTEGER UNIQUE,
                term TEXT
            )
            """
            cursor.execute(schema)
            schema = """
            CREATE TABLE IF NOT EXISTS known(
                term TEXT NOT NULL,
                card INTEGER NOT NULL,
                FOREIGN KEY (card)
                    REFERENCES cards (card)
                    ON UPDATE CASCADE
                    ON DELETE CASCADE
            )
            """
            cursor.execute(schema)
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
            cursor.execute(schema)

def verifyUserDatabase():
    with closing(sqlite3.connect(getUserDB())) as connection:
        with closing(connection.cursor()) as cursor:
            try:
                tables = cursor.execute("SELECT tbl_name FROM sqlite_master WHERE type='table'")
            except sqlite3.OperationalError:
                createUserDatabase()
                return
            if 'known' not in tables.fetchall():
                createUserDatabase()
    return True

def createDictDatabase():
    with closing(sqlite3.connect(getDictDB())) as connection:
        with closing(connection.cursor()) as cursor:
            schema = """
            CREATE TABLE IF NOT EXISTS terms(
                term TEXT,
                freq INTEGER,
                dict TEXT
            )
            """
            cursor.execute(schema)

def verifyDictDatabase():
    with closing(sqlite3.connect(getDictDB())) as connection:
        with closing(connection.cursor()) as cursor:
            try:
                tables = cursor.execute("SELECT tbl_name FROM sqlite_master WHERE type='table'")
            except sqlite3.OperationalError:
                createDictDatabase()
                return
            if 'terms' not in tables.fetchall():
                createDictDatabase()
    return True

def importYomichanFreqDict(path):
    with closing(sqlite3.connect(getDictDB())) as connection:
        with closing(connection.cursor()) as cursor:
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
            tableInDB = cursor.execute("SELECT dict FROM terms GROUP BY dict")
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
                    cursor.executemany("INSERT INTO terms VALUES (?,?,?)",newTerms)
                    termcount += len(terms)
            
            shutil.rmtree(tempFolder)
            connection.commit()
            return "Success, added " + str(termcount) + " terms"

def rmDictFromDB(name):
    with closing(sqlite3.connect(getDictDB())) as connection:
        with closing(connection.cursor()) as cursor:
            if name == "None":
                return
            connection.commit()
            cursor.execute("""
            DELETE FROM terms
            WHERE dict = ?
            """,(name,))
            connection.commit()

def getDicts():
    with closing(sqlite3.connect(getDictDB())) as connection:
        with closing(connection.cursor()) as cursor:
            res = cursor.execute("SELECT dict FROM terms GROUP BY dict")
            return res.fetchall() 

def addCardsToUserDB(cards):
    with closing(sqlite3.connect(getUserDB())) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.executemany("INSERT INTO cards VALUES (?,?)",cards)
            connection.commit()

def addSortedCards(cards):
    with closing(sqlite3.connect(getUserDB())) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.executemany("INSERT INTO sorted VALUES (?,?)",cards)
            connection.commit()

def clearSortedCards():
    with closing(sqlite3.connect(getUserDB())) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute("DELETE FROM sorted")
            connection.commit()

def addKnownCards(cards):
    with closing(sqlite3.connect(getUserDB())) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.executemany("""
            INSERT INTO known (term,card)
                SELECT term, card
                FROM cards
                WHERE card IN (?)
            """,[(c,) for c in cards])
            connection.commit()

def getCardsWithKnownTerms():
    with closing(sqlite3.connect(getUserDB())) as connection:
        with closing(connection.cursor()) as cursor:
            res = cursor.execute("""
            SELECT card
            FROM cards
            WHERE term IN (SELECT term FROM known)
            AND card NOT IN (SELECT card FROM known)
            """)
            return res.fetchall()

def getTermInDictDB(s) -> tuple:
    with closing(sqlite3.connect(getDictDB())) as connection:
        with closing(connection.cursor()) as cursor:
            dictName = getPrefs()['setDict']
            if dictName == "None":
                return ()
            res = cursor.execute("SELECT term, value FROM terms WHERE term='?' AND dict = '?'",(s,dictName))
            if res.fetchone() == None:
                return ()
            return res.fetchone()

def getCardsWithFreq():
    with closing(sqlite3.connect(getUserDB())) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute("ATTACH DATABASE ? AS source",(config('dictDB'),))
            res = cursor.execute("""
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
    with closing(sqlite3.connect(getUserDB())) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute("ATTACH DATABASE ? AS source",(config('dictDB'),))
            res = cursor.execute("""
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
    with closing(sqlite3.connect(getDictDB())) as connection:
        with closing(connection.cursor()) as cursor:
            res = cursor.execute("SELECT freq FROM terms ORDER BY freq DESC LIMIT 1")
            return res.fetchone()

def getCard(card):
    with closing(sqlite3.connect(getUserDB())) as connection:
        with closing(connection.cursor()) as cursor:
            res = cursor.execute("SELECT card,term FROM cards WHERE card = ?",(card,))
            return res.fetchone()

def getCards(cards):
    with closing(sqlite3.connect(getUserDB())) as connection:
        with closing(connection.cursor()) as cursor:
            res = cursor.execute("SELECT card,term FROM cards WHERE card IN (?)",[(c,) for c in cards])
            return res.fetchall()

def removeCardFromUserDB(id):
    with closing(sqlite3.connect(getUserDB())) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute("DELETE FROM cards WHERE card=?",(int(id),))
            connection.commit()

    
def resetUserDB():
    with closing(sqlite3.connect(getUserDB())) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute("DELETE FROM cards")
            cursor.execute("DROP TABLE cards")
            connection.commit()
            cursor.execute("DELETE FROM known")
            cursor.execute("DROP TABLE known")
            connection.commit()
            cursor.execute("DELETE FROM sorted")
            cursor.execute("DROP TABLE sorted")
            connection.commit()
            createUserDatabase()
            connection.commit()
