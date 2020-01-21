#
# ユーザ管理
#
import threading, uuid
from datetime import datetime
from lib.DBQueue import DBQueue

class UserHandle:
    def __init__(self):
        self.queue = DBQueue()
        self.identifier = uuid.uuid4()
        self.queue.initClient(self.identifier)
        self.dqEvent = threading.Event()

    #--未探索のユーザを検索
    def getUnTrackedUser(self, count=1):
        self.queue.enQueue(self.identifier, self.dqEvent, "SELECT * FROM userTable WHERE id=0 LIMIT ?", (count, ))
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
        self.queue.enQueue(self.identifier, self.dqEvent, "SELECT * FROM userTable WHERE modified<=? AND id>0 ORDER BY modified ASC LIMIT ?", (int(datetime.now().timestamp()) - time, count, ))
        self.dqEvent.wait()
        self.dqEvent.clear()
        users = self.queue.fetchrst(self.identifier)
        return users

    #--指定枚数のSaverに投げる画像を取得
    def getImages(self, count=1):
        self.queue.enQueue(self.identifier, self.dqEvent, "SELECT * FROM imageTable WHERE localPath=\"Nodata\" LIMIT ?", (count, ))
        self.dqEvent.wait()
        self.dqEvent.clear()
        images = self.queue.fetchrst(self.identifier)
        return images