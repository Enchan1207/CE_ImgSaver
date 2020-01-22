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
    pre_endReq = False #endReqをじかに受け取らない

    #--複数枚持ってきてバイナリ取得
    files = []
    while (not pre_endReq):
        images = uh.getImages(20)
        print("found:" + str(len(images)))
        if(len(images) == 0):
            pre_endReq = True

        for image in images:
            #--サーバから取得して待機
            print("get: " + image[4])
            files.append(saver.get(image))
            time.sleep(3)

            #--終了リクエストが来ても'このfor文は'止まらない
            if(endReq):
                pre_endReq = True

    #--適当に名前つけて保存(ここはendReqを無視する)
    saver.save(files)

    print("complete tracked image.")
    return 0

saveThread = threading.Thread(target=saveImages)
saveThread.setDaemon(True)

#--メインスレッドでは15分待つ、これはcronによる自動化のため
initThread.start()
updateThread.start()
saveThread.start()
try:
    time.sleep(15 * 60)
    endReq = True
except KeyboardInterrupt:
    print("終了リクエストを受け取りました。スレッドの終了を待機しています…")
    endReq = True
    initThread.join()
    updateThread.join()
    saveThread.join()
    print("終了リクエストが正常に受理されました。")
    exit(0)