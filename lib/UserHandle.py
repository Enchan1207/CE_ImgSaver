#
# ユーザ管理
#
from datetime import datetime
from lib.DBAccess import DBAccess

class UserHandle:
    def __init__(self):
        self.pdo = DBAccess("db/main.db")
    
    #--未探索のユーザを検索
    def getUnTrackedUsers(self):
        self.pdo.exec("SELECT * FROM userTable WHERE id=0", ())
        users = pdo.fetch()
        return users

    #--指定TwitterIDのユーザを追加
    def addTrackUsers(self, twids):
        for twid in twids:
            self.pdo.exec("INSERT INTO userTable VALUES(0,?,0,0,0)", (twid))

    #--次に処理するべきユーザを検索(クローリング後一定時間は対象から外れる)
    def getNext(self, count=1, time=10):
        self.pdo.exec("SELECT * FROM userTable WHERE modified<=? ORDER BY modified LIMIT ?", (int(datetime.now().timestamp()) - time, count, ))
        users = pdo.fetch()
        return users
