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
            print("process [" + users[0][1] + "] ...")
            result = self.cl.update(users[0], 2)
        else:
            result = -1

        rst = {"length": len(users), "result": result, "apistat": self.cl.getAPIStat()}
        return rst

    #--次に探索すべきユーザを取得し、データを更新
    def updateUsers(self):
        users = self.uh.getNext()
        rst = 0
        if(len(users) > 0):
            #--orで立てると、全てエラーなく終了しない限り必ず1になるので
            # 大まかなフェイルセーフになる
            print("update " + users[0][1])
            rst = rst or self.cl.update(users[0], 0)
            rst = rst or self.cl.update(users[0], 1)
        else:
            print("no target users found.")

        result = {"length": len(users), "result": rst, "apistat": self.cl.getAPIStat()}
        return result

    #--画像を保存する
    def saveImage(self):
        pdo = DBAccess("db/main.db")
        sql = "SELECT * FROM imageTable WHERE localPath=? ORDER BY post ASC LIMIT ?"
        pdo.exec(sql, ("Nodata", 1,))
        medias = pdo.fetch()

        if(len(medias) != 0):
            return self.sv.save(medias)
        else:
            return {"found": -1,"successed": -1}



        
