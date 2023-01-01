from aqt import mw
from .preferences import getPrefs
from . import db

def orderCards():
    col = mw.col
    config = getPrefs()
    cards = []
    if config['setDict'] == "None":
        return
    for noteType in config["filter"]:
        cards += col.find_cards("note: "+noteType["type"])
    configNoteMap = config["filter"]
    for card in cards:
        cardExp = card[configNoteMap[card.type]]
        dbExp =  db.getTermInDictDB(cardExp)
        if dbExp != ():
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
