from aqt import mw
col = mw.col
from . import preferences as prefs
from . import db

def getCardsFromConfigNoteTypes():
    notes = []
    for noteType in prefs.getJsonConfig()["filter"]:
        notes += col.find_cards("note:"+noteType["type"])
    return notes

def orderCards():
    config = prefs.getJsonConfig()
    cards = getCardsFromConfigNoteTypes()
    configNoteMap = config["filter"]
    with open("./user_data/dicts/"+config["freqDictFileName"]) as f:
        for card in cards:
            cardExp = card[configNoteMap[card.type]]
            dbExp =  db.getTermInDictDB(cardExp)
            if dbExp is not ():
                if db.checkIfTermInUserDB(cardExp):
                    note = card.note()
                    if config['tags']['known'] not in note.tags():
                        note.tags().append(config['tags']['known'])
                        col.update_note(note)
                        card.ord = 100000
                        col.update_card(card)
                else:
                    if card.ivl > 0:
                        db.addTermToUserDB(cardExp)
                    else:
                        note = card.note()
                        if config['tags']['ranked'] not in note.tags():
                            note.tags().append(config['tags']['ranked'])
                            col.update_note(note)
                        card.org = dbExp[1]
                        col.update_card(card)
