from anki.rsbackend import NotFoundError
from aqt import mw
from datetime import datetime
from .preferences import *
from .db import *

def getCardFromAnki(id):
    try:
        card = mw.col.get_card(id)
    except NotFoundError:
        removeCardFromUserDB(id)
        return None
    return card

def addCardsToDB():
    cardsToAdd = []
    for noteType in getPrefs()['filter']:
        cards = mw.col.find_cards("\"note:" + noteType['type'] + "\" -tag:" + getPrefs()['tags']['tracked'])
        for id in cards:
            card = getCardFromAnki(id)
            if card == None:
                removeCardFromUserDB(id)
            else:
                note = card.note()
                hasTags = True
                for tag in noteType['tags']:
                    if not note.has_tag(tag) and tag != "":
                        hasTags = False
                if hasTags:
                    assert noteType['field'] in note.keys(), "Failed to find field %s in note type with fields %s"%noteType['field']%note.keys()
                    expression = note[noteType['field']]
                    cardsToAdd.append([id,expression])
                    note.add_tag(getPrefs()['tags']['tracked'])
                    mw.col.update_note(note)
    addCardsToUserDB(cardsToAdd)

def markCardsAsKnown():
    known = mw.col.find_cards("tag:"+getPrefs()['tags']['tracked'] + " -is:new")
    dbKnown = getCardsWithKnownTerms()
    toClean = []
    if getGeneralOption('ignoreSusLeech'):
        exclude = mw.col.find_cards("is:suspended tag:leech tag:"+getPrefs()['tags']['tracked'])
        for id in exclude:
            known.remove(id)
            cleanCard(id)
    for id in known:
        if id not in dbKnown:
            card = getCardFromAnki(id)
            card.note().add_tag(getPrefs()['tags']['known'])
            mw.col.update_note(card.note())
        else:
            toClean.append(id)
    cleanCards(toClean)
    addKnownCards(known)

def pushKnownNewCardsBack():
    known = getCardsWithKnownTerms()
    for id in known:
        card = getCardFromAnki(id[0])
        if card:
            assert card, "None card"
            card.note().add_tag(getPrefs()['tags']['pushed'])
            if card.due != 200000:
                card.due = 200000
                mw.col.update_card(card)
                mw.col.update_note(card.note())
        else:
            cleanCard(id)

def pushBackCardsWithNoFreq():
    tracked = getCardsWithoutFreq()
    for id in tracked:
        card = getCardFromAnki(id[0])
        if card:
            if card.type == 0 and not card.note().has_tag(getPrefs()['tags']['pushed']):
                if card.due != 100000:
                    card.due = 100000
                    card.note().add_tag(getPrefs()['tags']['pushed'])
                    mw.col.update_note(card.note())
                    mw.col.update_card(card)
        else:
            cleanCard(id)

def orderCardsInDB():
    tracked = getCardsWithFreq()
    cards = []
    toClean = []
    highest = getHighestFreqVal()[0] + 1
    for (id,freq) in tracked:
        card = getCardFromAnki(id)
        if card:
            if card.type == 0 and not card.note().has_tag(getPrefs()['tags']['pushed']):
                if getPrefs()['dictStyle'] == 'Rank':
                    if card.due != freq:
                        card.due = freq
                else:
                    if card.due != highest - freq:
                        card.due = highest - freq
                card.note().add_tag(getPrefs()['tags']['sorted'])
                mw.col.update_note(card.note())
                mw.col.update_card(card)
                cards.append((id,getPrefs()['setDict']))
        else:
            toClean.append(id)
    cleanCards(toClean)
    addSortedCards(cards)

def cleanUpdatedCards():
    toClean = []
    for noteType in getPrefs()['filter']:
        updated = mw.col.find_cards("edited:"+str(getDaysSinceLastUpdate())
                                        + " tag:" + getPrefs()['tags']['tracked']
                                        + " \"note:" + noteType['type'] + "\"")
        for id in updated:
            card =  getCardFromAnki(id)
            if card != None:
                term = card.note()[noteType['field']]
                assert term, "id:" + str(id)
                if term != getCard(id)[1]:
                    toClean.append(id)
            else:
                toClean.append(id)

        
    cleanCards(toClean)

def cleanCards(ids):
    for id in ids:
        cleanCard(id)

def cleanCard(id: int):
    removeCardFromUserDB(id)
    card = getCardFromAnki(id)
    if card != None:
        for tag in getPrefs()['tags'].values():
            card.note().remove_tag(tag)
        mw.col.update_note(card.note())

def cleanSorted():
    clearSortedCards()
    for id in mw.col.find_cards("tag:" + getPrefs()['tags']['sorted']):
        card = getCardFromAnki(id)
        card.note().remove_tag(getPrefs()['tags']['sorted'])
        mw.col.update_note(card.note())

def recalculate():
    if getGeneralOption('refresh'):
        cleanUserData()
        setGeneralOption('refresh',False)
    cleanUpdatedCards()
    cleanSorted()
    addCardsToDB()
    markCardsAsKnown()
    pushKnownNewCardsBack()
    pushBackCardsWithNoFreq()
    orderCardsInDB()
    setPref('lastUpdate',datetime.today().isoformat())
    setPref('lastSortedDict',getPrefs()['setDict'])

def cleanUserData():
    resetUserDB()
    for tag in getPrefs()['tags'].values():
        notes = mw.col.find_notes("tag:" + tag)
        for id in notes:
            note = mw.col.get_note(id)
            note.remove_tag(tag)
            mw.col.update_note(note)
