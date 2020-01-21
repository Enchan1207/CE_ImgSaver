#
# エラーハンドル
#

from lib.DBQueue import DBQueue
from datetime import datetime
import threading, uuid

class ErrHandle:
    def __init__(self):
        self.queue = DBQueue()
        self.identifier = uuid.uuid4()
        self.queue.initClient(self.identifier)
        self.dqEvent = threading.Event()

    def addError(self, message):
        self.queue.enQueue(self.identifier, self.dqEvent, "INSERT INTO errorTable VALUES(0, ?, ?)", (int(datetime.now().timestamp()), message,))
        self.dqEvent.wait()
        self.dqEvent.clear()