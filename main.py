#
# Twitter画像ダウンローダー
#
from lib.UserHandle import UserHandle
from lib.DBQueue import DBQueue
from lib.Clawler import Clawler
import time
import threading
import logging

#--ロギング
logging.basicConfig(filename='logfile/logger.log', level=logging.INFO)

#--デキュースレッドを立てる
def dequeueThread():
    queue4Dequeue = DBQueue()
    queue4Dequeue.connect("db/main.db")
    queue4Dequeue.deQueue(120)

dqthread = threading.Thread(target=dequeueThread)
dqthread.setDaemon(True) #デーモンスレッド化しないとタイムアウトするまで終わらなくなる
dqthread.start()

#--未探索のユーザを探索するスレッドを立てる
def initRecord():
    logging.info("start to init untracked user record")
    clawler = Clawler("db/main.db")
    uh = UserHandle()
    untrackedList = uh.getUnTrackedUsers()
    for user in untrackedList:
        clawler.update(user, 2)
        logging.info("tracked:" + user[1])
        time.sleep(3)
        
initThread = threading.Thread(target=initRecord)
initThread.setDaemon(True)
initThread.start()

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        exit(0)


