#
# 自動化されるタスク
#
from lib.DBAccess import DBAccess
from lib.Clawler import Clawler
from lib.Saver import Saver
from lib.UserHandle import UserHandle
from datetime import datetime

class Tasks:
    def __init__(self):
        self.cnt = 0
        self.uh = UserHandle() #ユーザハンドラ
        self.cl = Clawler("db/main.db") #クローラ
        self.sv = Saver("db/main.db", "D:/KigPhotos") #セーバ

    #--
    def func(self):
        print(datetime.now().timestamp())
        self.cnt += 1
        if(self.cnt >= 10):
            return 1
        else:
            return 0

    #--未探索のユーザを処理する
    def initUTUsers(self):
        users = self.uh.getUnTrackedUsers()
        if(len(users) != 0):
            result = self.cl.update(users[0], 2)
        else:
            result = -1

        rst = {"length": len(users), "result": result, "apistat": self.cl.getAPIStat()}
        return rst

    #--次に探索すべきユーザを取得し、データを更新
    def updateUsers(self):
        users = self.uh.getNext()
        if(len(users) != 0):
            self.cl.update(users[0], 0)
            self.cl.update(users[0], 1)

    #--画像を保存する
    def saveImage(self):
        #--保存できる画像はあるか?
        sql = "SELECT * FROM imageTable WHERE localPath=? ORDER BY post ASC LIMIT ?"
        pdo.exec(sql, ("Nodata", 20,))
        medias = pdo.fetch()

        if(len(medias) != 0):
            self.sv.save(medias)

        return self.sv.getStat()





        
