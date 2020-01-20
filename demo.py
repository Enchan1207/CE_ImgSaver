#
# Twitter画像ダウンローダー　デモ
#
import time
import threading
from datetime import datetime
from lib.Tasks import Tasks
from lib.DBQueue import DBQueue

task = Tasks()

#--未探索ユーザ探索スレッド起動
# エラーが発生しておらず
# lengthが0でなければ続ける
def init_UTU_Thread():
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

#--探索済みユーザ更新スレッド起動
# 更新できるユーザが存在し
# 更新鮮度が十分下がっていれば続ける
def upd_TU_Thread():
    cnt = 0
    print("--- update tracked users... ---")
    ud_result = task.updateUsers()
    while (ud_result['length'] > 0) and (ud_result['result'] == 0):
        cnt += 1
        print(ud_result['apistat'])
        ud_result = task.updateUsers()
    if(ud_result['result'] > 0):
        print("Demo: Some error has occured.")
    else:
        print("updated  " + str(cnt) + " users.")

#--画像保存スレッド起動
# 画像が見つかり、同時保存枚数が500以下なら繰り返す
def sv_TI_Thread():
    cnt = 0
    print("--- save tracked images... ---")
    si_result = task.saveImage()
    while (si_result['found'] > 0) and (cnt < 500): 
        cnt += 1
        time.sleep(3)
        si_result = task.saveImage()
    print("saved " + str(cnt) + " images.")


#
# DB並行処理
#

#--デキュースレッドを立てる
def dequeueThread():
    queue4Dequeue = DBQueue()
    queue4Dequeue.connect("db/main.db")
    queue4Dequeue.deQueue(120)

dqthread = threading.Thread(target=dequeueThread)
dqthread.setDaemon(True) #デーモンスレッド化しないとタイムアウトするまで終わらなくなる
dqthread.start()

thr_iutu = threading.Thread(target=init_UTU_Thread)
thr_utt = threading.Thread(target=upd_TU_Thread)
thr_stt = threading.Thread(target=sv_TI_Thread)

thr_iutu.start()
thr_utt.start()
thr_stt.start()

#TODO: DBAccess.execをDBQueueに対応させる