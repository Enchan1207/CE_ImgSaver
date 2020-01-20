#
# ユーザ管理
#
import threading
from datetime import datetime
from lib.DBQueue import DBQueue

class UserHandle:
    def __init__(self):
        self.queue = DBQueue()
        self.identifier = str(int(datetime.now().timestamp()))
        self.queue.initClient(self.identifier)
        self.dqEvent = threading.Event()
    
    #--未探索のユーザを検索
    def getUnTrackedUsers(self):
        self.queue.enQueue(self.identifier, self.dqEvent, "SELECT * FROM userTable WHERE id=0")
        self.dqEvent.wait()
        self.dqEvent.clear()
        users = self.queue.fetchrst(self.identifier)
        return users

    #--指定TwitterIDのユーザを追加
    def addTrackUsers(self, twids):
        for twid in twids:
            self.queue.enQueue(self.identifier, self.dqEvent, "INSERT INTO userTable VALUES(0,?,0,0,0)", (twid,))
        self.dqEvent.wait()
        self.dqEvent.clear()

    #--次に処理するべきユーザを検索(クローリング後一定時間は対象から外れる)
    def getNext(self, count=1, time=10):
        self.queue.enQueue(self.identifier, self.dqEvent, "SELECT * FROM userTable WHERE modified<=? ORDER BY modified ASC LIMIT ?", (int(datetime.now().timestamp()) - time, count, ))
        self.dqEvent.wait()
        self.dqEvent.clear()
        users = self.queue.fetchrst(self.identifier)
        return users
