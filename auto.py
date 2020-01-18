#
# 自動化したい
#
import threading, time
from datetime import datetime
from lib.Tasks import Tasks

ts = Tasks()
wt = 3
event = threading.Event()
while not event.wait(wt):
    rst = ts.func()
    if(rst != 0):
        event.set()
