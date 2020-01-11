# CE_ImgSaver

## OverView
A simple twitter media dounloader written by Python and sqlite.  
linked account: [@CollectEnchan](twitter.com/CollectEnchan)  

## Contents
 * main.py: main source (but it's rarely used.)
 * db/
    * recovery.sql: sql file for recovery (first, you use it on sqlite3 to make `data.db`)
    * data.db(ignored): main database
 * lib/
    * DBAccess.py: DB control
    * ErrHandle.py: Error handling
    * GetTl.py: getting twitter timeline
    * TweetHandle.py: Tweet handling
    * config.py(ignored): TwitterAPI configuration

## Usage
### Installation
**NOTE:** this software requires python modules shown below and some default modules:

 * oauthlib
 * requests
 * requests-oauthlib

if you don't have them, install using `pip`.  

 1. clone this repository.
 2. exec `sqlite3 data.db < recovery.sql` in `db/`.
 3. `python main.py` to start demo.
