#
# Twitter画像ダウンローダー
#
from lib.UserHandle import UserHandle
from lib.DBQueue import DBQueue
from lib.Clawler import Clawler
from lib.Saver import Saver
import time, threading, logging

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
    logging.info("complete tracking new users.")
        
initThread = threading.Thread(target=initRecord)
initThread.setDaemon(True)
initThread.start()

#--レコード初期化ずみのユーザを更新するスレッドを立てる
def updateUser():
    logging.info("start to update tracked user data")
    clawler = Clawler("db/main.db")
    uh = UserHandle()
    target = uh.getNext()
    while (len(target) > 0):
        clawler.update(target[0], 0)
        clawler.update(target[0], 1)
        logging.info("update:" + target[0][1])
        time.sleep(3)
        target = uh.getNext()

    logging.info("complete update tracked users in this phase.")

updateThread = threading.Thread(target=updateUser)
updateThread.setDaemon(True)
updateThread.start()

#--画像を保存するスレッドを立てる
def saveImages():
    logging.info("save tracked image")
    saver = Saver("db/main.db", "img")
    uh = UserHandle()
    while True:
        images = uh.getImages(40)
        if(len(images) > 0):
            saver.save(images)
            print("Saved.")
            logging.info("saved")
        time.sleep(3)

    logging.info("complete save images in this phase.")

saveThread = threading.Thread(target=saveImages)
saveThread.setDaemon(True)
saveThread.start()

#--メインスレッドは待機しつつCtrl+Cを待つ、終了リクエストが飛んできたらEndReqを立てる
while True:
    try:
        time.sleep(60 * 15)
    except KeyboardInterrupt:
        exit(0)

