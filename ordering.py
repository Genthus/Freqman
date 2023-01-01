from aqt import mw
from .preferences import getPrefs
from .db import *

def addCardsToDB():
    cardsToAdd = []
    for noteType in getPrefs()['filter']:
        cards = mw.col.find_cards("note:" + noteType['type'] + " -tag:" + getPrefs()['tags']['tracked'])
        for id in cards:
            card = mw.col.get_card(id)
            if card == None:
                break
            note = card.note()
            assert noteType['field'] in note.keys(), "Failed to find field %s in note type with fields %s"%noteType['field']%note.keys()
            expression = note[noteType['field']]
            cardsToAdd.append([id,expression])
            note.add_tag(getPrefs()['tags']['tracked'])
            mw.col.update_note(note)
    addCardsToUserDB(cardsToAdd)

def markCardsAsKnown():
    known = mw.col.find_cards("tag:"+getPrefs()['tags']['tracked'] + " -is:new")
    for id in known:
        card = mw.col.get_gard(id)
        card.note().add_tag(getPrefs()['tags']['known'])
        mw.col.update_note(card.note())
    addKnownCards(known)

def pushKnownNewCardsBack():
    known = getKnownCards()
    for cardType in getPrefs()['filter']:
        new = mw.col.find_cards("tag:" + getPrefs()['tags']['tracked'] 
                                    + " is:new" 
                                    + " -tag:" + getPrefs()['tags']['known']
                                    + " note:" + cardType['type'])
        for id in new:
            card = mw.col.get_card(id)
            if card == None:
                break
            if cardType['field'] not in card.note().keys():
                break
            expression = card.note()[cardType['field']]
            if expression in known:
                card.note().add_tag(getPrefs()['tags']['known'])
                card.ord = 100000
                mw.col.update_card(card)
                mw.col.update_note(card.note())

def orderCardsInDB():
    tracked = getCardsWithFreq()
    for (id,freq) in tracked:
        card = mw.col.get_card(id)
        card.ord = freq
        card.note().add_tag(getPrefs()['tags']['sorted'])
        mw.col.update_note(card.note())
    addSortedCards(mw.col.find_cards("tag:"+getPrefs()['tags']['sorted']))

def cleanUpdatedCards():
    updated = getUpdatedCards()
    for id in updated:
        card = mw.col.get_card(id)
        if card == None:
            break
        for tag in getPrefs()['tags'].values:
            card.note().remove_tag(tag)

def recalculate():
    cleanUpdatedCards()
    addCardsToDB()
    orderCardsInDB()
    markCardsAsKnown()
    pushKnownNewCardsBack()
