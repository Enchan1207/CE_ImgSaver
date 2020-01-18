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
cnt = 0

#--探索済みユーザ更新スレッド起動
# 更新できるユーザが存在し
# 更新鮮度が十分下がっていれば続ける
print("--- update tracked users... ---")
ud_result = task.updateUsers()
while (ud_result['length'] > 0) and (ud_result['result'] == 0):
    cnt += 1
    time.sleep(3)
    print(ut_result['apistat'])
    ud_result = task.updateUsers()
if(ut_result['result'] > 0):
    print("Demo: Some error has occured.")
else:
    print("updated  " + str(cnt) + " users.")
cnt = 0

#--画像保存スレッド起動
# 画像が見つかり、同時保存枚数が500以下なら繰り返す
print("--- save tracked images... ---")
si_result = task.saveImage()
while (si_result['found'] > 0) and (cnt < 500): 
    cnt += 1
    time.sleep(3)
    si_result = task.saveImage()
print("saved " + str(cnt) + " images.")
    
#TODO:なんで画像が重複する?
#TODO:過去ツイを漁りきった判定