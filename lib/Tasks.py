#
# 自動化されるタスク
#
from lib.Clawler import Clawler
from lib.Saver import Saver
from lib.UserHandle import UserHandle
from datetime import datetime
import threading

class Tasks:
    def __init__(self):
        self.cnt = 0

    #--未探索のユーザを処理する
    def initUTUsers(self):
        usrhd = UserHandle() #ユーザハンドラ
        clawler = Clawler("db/main.db") #クローラ

        users = usrhd.getUnTrackedUsers()
        if(len(users) != 0):
            print("process [" + users[0][1] + "] ...")
            result = clawler.update(users[0], 2)
        else:
            result = -1

        rst = {"length": len(users), "result": result, "apistat": clawler.getAPIStat()}
        return rst

    #--次に探索すべきユーザを取得し、データを更新
    def updateUsers(self):
        usrhd = UserHandle() #ユーザハンドラ
        clawler = Clawler("db/main.db") #クローラ

        users = usrhd.getNext()
        rst = 0
        if(len(users) > 0):
            #--orで立てると、全てエラーなく終了しない限り必ず1になるので
            # 大まかなフェイルセーフになる
            print("update " + users[0][1])
            rst = rst or clawler.update(users[0], 0)
            rst = rst or clawler.update(users[0], 1)
        else:
            print("no target users found.")

        result = {"length": len(users), "result": rst, "apistat": clawler.getAPIStat()}
        return result

    """
    #--画像を保存する(ちょっとpdoとの兼ね合いが難しいので保留)
    def saveImage(self):
        pdo = DBAccess("db/main.db")
        saver = Saver("db/main.db", "/mnt/usb1/kigurumi/") #セーバ
        sql = "SELECT * FROM imageTable WHERE localPath=? ORDER BY post ASC LIMIT ?"
        pdo.exec(sql, ("Nodata", 1,))
        medias = pdo.fetch()

        if(len(medias) != 0):
            return saver.save(medias)
        else:
            return {"found": -1,"successed": -1}
    """