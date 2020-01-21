#
# Twitter画像ダウンローダー
#
from lib.UserHandle import UserHandle
from lib.DBQueue import DBQueue
from lib.Clawler import Clawler
from lib.Saver import Saver
import time, threading

endReq = False #終了リクエスト

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
    print("start to init untracked user record")
    clawler = Clawler("db/main.db")
    uh = UserHandle()
    target = uh.getUnTrackedUser()
    while (len(target) > 0) and (not endReq):
        clawler.update(target[0], 2)
        print("track:" + target[0][1])
        time.sleep(3)
        target = uh.getUnTrackedUser()

    print("complete tracking new users.")
        
initThread = threading.Thread(target=initRecord)
initThread.setDaemon(True)

#--レコード初期化済みのユーザを更新するスレッドを立てる
def updateUser():
    print("start to update tracked user data")
    clawler = Clawler("db/main.db")
    uh = UserHandle()
    target = uh.getNext()
    while (len(target) > 0) and (not endReq):
        clawler.update(target[0], 0)
        clawler.update(target[0], 1)
        print("update:" + target[0][1])
        time.sleep(3)
        target = uh.getNext()

    print("complete update tracked users in this phase.")

updateThread = threading.Thread(target=updateUser)
updateThread.setDaemon(True)

#--画像を保存するスレッドを立てる
def saveImages():
    print("save tracked image")
    saver = Saver("db/main.db", "img")
    uh = UserHandle()
    while not endReq:
        images = uh.getImages(40)
        if(len(images) > 0):
            saver.save(images)
            print("Saved.")
            print("saved")
        time.sleep(3)

    print("complete save images in this phase.")

saveThread = threading.Thread(target=saveImages)
saveThread.setDaemon(True)

#--メインスレッドでは15分待つ、これはcronによる自動化のため
initThread.start()
updateThread.start()
# saveThread.start()
try:
    time.sleep(15 * 60)
    endReq = True
except KeyboardInterrupt:
    print("終了リクエストを受け取りました。スレッドの終了を待機しています…")
    endReq = True
    initThread.join()
    updateThread.join()
    # saveThread.join()
    print("終了リクエストが正常に受理されました。")
    exit(0)