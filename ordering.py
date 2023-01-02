from aqt import mw
from .preferences import getPrefs, setGeneralOption, setPref, getGeneralOption
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
    if getGeneralOption('ignoreSusLeech'):
        known = mw.col.find_cards("tag:"+getPrefs()['tags']['tracked'] + " -is:new -tag:leech -is:suspended")
    for id in known:
        card = mw.col.get_card(id)
        card.note().add_tag(getPrefs()['tags']['known'])
        mw.col.update_note(card.note())
    addKnownCards(known)

def pushKnownNewCardsBack():
    known = getCardsWithKnownTerms()
    for id in known:
        card = mw.col.get_card(id[0])
        assert card, "None card"
        card.note().add_tag(getPrefs()['tags']['known'])
        card.due = 200000
        mw.col.update_card(card)
        mw.col.update_note(card.note())

def orderCardsInDB():
    tracked = getCardsWithFreq()
    cards = []
    for (id,freq) in tracked:
        card = mw.col.get_card(id)
        if card.type == 0 and not card.note().has_tag(getPrefs()['tags']['known']):
            card.due = freq
            card.note().add_tag(getPrefs()['tags']['sorted'])
            mw.col.update_note(card.note())
            mw.col.update_card(card)
            cards.append((id,getPrefs()['setDict']))
    for id in mw.col.find_cards("tag:" + getPrefs()['tags']['sorted']):
        if id not in cards:
            card = mw.col.get_card(id)
            card.note().remove_tag(getPrefs()['tags']['sorted'])
    addSortedCards(cards)

def cleanUpdatedCards():
    # TODO account for card deletion and stuff like that
    updated = getUpdatedCards()
    for id in updated:
        card = mw.col.get_card(id)
        if card == None:
            removeCardFromUserDB(id)
        for tag in getPrefs()['tags'].values:
            card.note().remove_tag(tag)
        mw.col.update_note(card.note())

def cleanSorted():
    clearSortedCards()
    for id in mw.col.find_cards("tag:" + getPrefs()['tags']['sorted']):
        card = mw.col.get_card(id)
        card.note().remove_tag(getPrefs()['tags']['sorted'])

def recalculate():
    cleanUpdatedCards()
    addCardsToDB()
    if getPrefs()['setDict'] != getPrefs()['lastSortedDict']:
        cleanSorted()
        setGeneralOption('refresh',False)
    # TODO remove tags
    markCardsAsKnown()
    pushKnownNewCardsBack()
    orderCardsInDB()
    setPref('lastSortedDict', getPrefs()['setDict'])

def cleanUserData():
    resetUserDB()
    for tag in getPrefs()['tags'].values():
        notes = mw.col.find_notes("tag:" + tag)
        for id in notes:
            note = mw.col.get_note(id)
            note.remove_tag(tag)
            mw.col.update_note(note)
