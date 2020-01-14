#
# Twitter画像ダウンローダー
#
from lib.DBAccess import DBAccess
from lib.Clawler import Clawler
from lib.Saver import Saver
from datetime import datetime

pdo = DBAccess("db/main.db")

cl = Clawler("db/main.db")
#--新規ユーザをuserDBに追跡対象として追加
twid = input("type TwitterID if needed >")
if(twid != ""):
    userTuple = (0, twid, int(datetime.now().timestamp()), -1, -1)
    pdo.exec("INSERT INTO userTable VALUES(?,?,?,?,?)", userTuple)
    cl.update(userTuple, 2)

#--クローリング対象のユーザは存在するか?
time = 60 #クローリング対象に入るまでの時間 ここで指定した時間が経過するまで同じユーザに対するリクエストは行われない
pdo.exec("SELECT * FROM userTable WHERE modified<=? ORDER BY modified LIMIT 1", (int(datetime.now().timestamp()) - time,))
user = pdo.fetch()

if(len(user) != 0):
    # 0を指定すると過去ツイ 1を指定すると新規ツイを探索
    cl.update(user[0], 0)
    cl.update(user[0], 1)
else:
    print("no target user found.")

#--保存できる画像はあるか?
sv = Saver("db/main.db", "D:/KigPhotos")
sql = "SELECT * FROM imageTable WHERE localPath=? ORDER BY post ASC LIMIT ?"
pdo.exec(sql, ("Nodata", 20,))
medias = pdo.fetch()

if(len(medias) != 0):
    saved = sv.save(medias) #savedは試行結果
else:
    print("no target image found.")

#--最後にAPIStatを表示
print("---")
print(cl.getAPIStat())
print("---")
print(sv.getStat())