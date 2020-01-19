# CE_ImgSaver

## OverView
A simple twitter media downloader written by Python and sqlite.  
linked account: [@CollectEnchan](twitter.com/CollectEnchan)  

## Contents
 * demo.py: demo source
 * db/
    * recovery.sql: sql file for recovery
    * data.db(ignored): main database
    * (some batch or shell file is used to observe using `watch` or `cat`.)
 * lib/
    * Clawler.py: timeline updater
    * config.py(ignored): TwitterAPI configuration
    * DBAccess.py: DB control
    * ErrHandle.py: Error handling
    * GetTl.py: getting twitter timeline
    * Saver.py: saving timelines medias
    * Tasks.py: tasks for automation
    * TweetHandle.py: Tweet handling
    * UserHandle.py: User  handling

## Documentation
In details, read [documentation](documentation/index.md).

## Usage
### Installation
**NOTE:** this software requires python modules shown below and some default modules:

 * requests
 * requests-oauthlib

if you don't have them, install using `pip`.  

 1. clone this repository.
 1. `cd db`.
 1. run `sqlite3 main.db < main.sql`.
 1. run `add.sh (username)` or `add.bat (username)` to add new data to `main.db`.

### Configuration
Run `python demo.py` without `lib/config.py`, process will end with error:

    from lib.config import OAConfig
    ModuleNotFoundError: No module named 'lib.config'
    
you need Twitter API registration and some API key.  
make `config.py` and write some code shown below:

    class OAConfig:
        CONSUMER_KEY = "{API key}"
        CONSUMER_SECRET = "{API secret key}"
        ACCESS_TOKEN = "{Access token}"
        ACCESS_TOKEN_SECRET = "{Access token secret}"

You may need to change save path.  
To change this, overwrite line 15 of `lib/Tasks.py`.

### Execute
`python demo.py` to run demo.

## LICENSE
All files on this repository is published under the MIT license.  
**NOTE:** The copyright of the data collected using the programs in this repository is held by the user who posted the tweet.  
Be careful with data handling and do not infringe other users copyright.  