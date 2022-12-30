from aqt import mw
col = mw.col
from . import preferences as prefs
import json

def getCardsFromConfigNoteTypes():
    notes = []
    for noteType in prefs.getJsonConfig()["filter"]:
        notes += col.find_cards("note:"+noteType["type"])
    return notes

def orderCards():
    count = 1
    cards = getCardsFromConfigNoteTypes()
    configNoteMap = prefs.getJsonConfig()["filter"]
    with open("./user_data/dicts/"+prefs.getJsonConfig()["freqDictFileName"]) as f:
        for card in cards:
            cardExp = card[configNoteMap[card.type]]
            if cardExp in freqList:
                if cardExp in db:
                    # tag card as already known
                else:
                    #if card not unseen, add to db
                    if card.ivl > 0:
                        # add to db
                    else:
                        card.ord = db.position
            else:
                # tag card as not in freq list
            col.update_card(card)
