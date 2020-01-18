#
# Twitter画像ダウンローダー　デモ
#
from datetime import datetime
import time

from lib.DBAccess import DBAccess
from lib.Clawler import Clawler
from lib.Saver import Saver
from lib.UserHandle import UserHandle

from lib.Tasks import Tasks
task = Tasks()

#--未探索ユーザ探索スレッド起動
# エラーが発生しておらず
# lengthが0でなければ続ける
print("--- process untracked users... ---")
ut_result = task.initUTUsers()
cnt = 0
while (not ut_result['length'] == 0) and (ut_result['result'] == 0):
    cnt += 1
    time.sleep(3)
    print(ut_result['apistat'])
    ut_result = task.initUTUsers()
if(ut_result['result'] > 0):
    print("Demo: Some error has occured.")
else:
    print("processed " + str(cnt) + " new users.")

#--画像保存スレッド起動
# 画像が見つかり、同時保存枚数が500以下なら繰り返す
si_result = task.saveImage()
svcnt = 0
while not(si_result['found'] == 0) and svcnt < 500:
    svcnt += si_result['found']
    time.sleep(3)
    si_result = task.saveImage()
    

#TODO:過去ツイを漁りきった判定