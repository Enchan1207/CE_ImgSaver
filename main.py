#
# Twitter画像ダウンローダー
#
from lib.DBAccess import DBAccess
from lib.Clawler import Clawler
from datetime import datetime

pdo = DBAccess("db/main.db")
cl = Clawler("db/main.db")

#--クローリング対象のユーザは存在するか?
time = 5 #クローリング対象に入るまでの時間 ここで指定した時間が経過するまで同じユーザに対するリクエストは行われない
pdo.exec("SELECT * FROM userTable WHERE modified<=? ORDER BY modified LIMIT 1", (int(datetime.now().timestamp()) - time,))
user = pdo.fetch()

if(len(user) != 0):
    cl.update(user[0], 0) # 0を指定すると過去ツイ 1を指定すると新規ツイを探索