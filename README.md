# Freqman

Anki addon to sort cards according to a frequency dictionary

## Status

in MVP development, still not ready to deploy for public use.

## Features

Import your yomichan frequency dictionaries into the addon.
Sort the selected card types by frequency or rank.

## Setup

WIP

## Usage

WIP

## Backstory

This is basically a replacement for morphman since its development has not kept up with recent anki releases.
I also use morphman in a very particular way that ignores its main features,
I'm making this to remove bloat and simplify the process.

## Structure

User config goes in config.json at the root of the addon, this is managed by anki.

The user files go into the folder user_files, which contains the databases.

### DBs

user.db: user's known terms go in here
dict.db: imported dictionaries go in here
