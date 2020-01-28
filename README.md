# CE_ImgSaver

## OverView
A simple twitter media downloader written by Python and sqlite.  
linked account: [@CollectEnchan](twitter.com/CollectEnchan)  

## Contents
 * main.py: main source
 * db/
    * recovery.sql: sql file for recovery
    * data.db(ignored): main database
    * ~~(some batch or shell file is used to observe using `watch` or `cat`.)~~ **Ignored**
 * lib/
    * Clawler.py: timeline updater
    * Command.py: DM Command parse and execute
    * config.py(ignored): TwitterAPI configuration
    * DBAccess.py: DB control
    * DBQueue.py: DB queue control
    * DMComm.py: DM Communication
    * ~~ErrHandle.py: Error handling~~ **Error handling is replaced by logging module.**
    * GetTl.py: getting twitter timeline
    * Saver.py: saving timelines medias
    * ~~Tasks.py: tasks for automation~~ **All thread process is written in main.py**
    * TweetHandle.py: Tweet handling
    * UserHandle.py: User  handling

## Documentation
In details, read [documentation](documentation/index.md).

## Usage
### Installation
**NOTE:** this software requires python modules shown below and some default modules:

 * requests

if you don't have them, install using `pip`.  

 1. clone this repository.
 1. `cd db`.
 1. run `sqlite3 main.db < main.sql`.

### Configuration
Run `python main.py` without `lib/config.py`, process will end with error:

    from lib.config import OAConfig
    ModuleNotFoundError: No module named 'lib.config'
    
you need Twitter API registration and some API key.  
make `config.py` and write some code shown below:

    class OAConfig:
        CONSUMER_KEY = "{API Key}"
        CONSUMER_SECRET = "{API Key Secret}"
        ACCESS_TOKEN = "{Access Token}"
        ACCESS_TOKEN_SECRET = "{Access Token Secret}"

    class DMConfig:
        ID_MASTER = "{Admins Recipient ID}"

    class PathConfig:
        PATH_IMGSAVE = "{image-saving path}"
        PATH_LOGOUTPUT = "log path"

~~You may need to change save path.~~  
~~To change this, overwrite line 15 of `lib/Tasks.py`.~~  
you can change image-saving path and log path to modify `lib/config.py`(on [#2](https://github.com/Enchan1207/CE_ImgSaver/issues/2)).  

### Execute
`python main.py` to run demo.

## LICENSE
## Libraries License
* [psf/requests](https://github.com/psf/requests)
  > Requests
  > A simple, yet elegant HTTP library. [https://requests.readthedocs.io](https://requests.readthedocs.io)
  >
  > Copyright 2019 Kenneth Reitz  
  > Apache 2.0 License
  > https://github.com/psf/requests/blob/master/LICENSE
  > https://www.apache.org/licenses/LICENSE-2.0


## LICENCE
All files except those described in the Libraries License section are distributed under the MIT license.