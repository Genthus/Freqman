# Freqman

Anki addon to sort cards according to a frequency dictionary

## Status

It mostly works, some things are a little messy so I advice to make backups often.
If you have an issue or feature you want to see added, please do say something by opening an issue in the [Github repo](https://github.com/Genthus/Freqman)

## Features

Import your yomichan frequency dictionaries into the addon.
Sort the selected card types by frequency or rank.

## Usage

### Download

Clone this repository

>Windows

`git clone -main https://github.com/Genthus/Freqman %APPDATA%\Roaming\Anki2\addons21`

>Other

`git clone -main https://github.com/Genthus/Freqman ~/.local/share/Anki2/addons21`

OR download the addon into your addons folder

>Windows:
`%APPDATA%\Roaming\Anki2\addons21`

>Other:
`~/.local/share/Anki2/addons21`

### Setup

1. Restart Anki
2. Open Freqman->Preferences from the main Anki window menu
3. Set your note types in the Note Filter section
4. Import a dictionary from the Dictionary Selection section
5. Select dictionary
6. Apply changes
7. Reorder your cards by clicking Freqman->Reorder cards from the main Anki window menu

## Troubleshooting

### First aid

Open the preferences menu and reset you database and tags, if that doesn't work, reset your settings.
If this fixes it you can blame it on my bad future-proofing.

### Other

Please open an issue in the [Github repo](https://github.com/Genthus/Freqman)

## Backstory

This is basically a replacement for morphman since its development has not kept up with recent anki releases.
I also use morphman in a very particular way that ignores its main features,
I'm making this to remove bloat and simplify the process.

## Structure

User config goes in config.json at the root of the addon, this is managed by anki.

The user files go into the folder user_files, which contains the databases.

### DBs

>user.db

user's known terms go in here
>dict.db

imported dictionaries go in here
