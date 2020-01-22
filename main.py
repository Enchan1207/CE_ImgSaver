#
# Twitter画像ダウンローダー
#
from lib.UserHandle import UserHandle
from lib.DBQueue import DBQueue
from lib.Clawler import Clawler
from lib.Saver import Saver
import time, threading, logging

endReq = False #終了リクエスト
with open("process.log", "a") as f:
    pass
logging.basicConfig(filename="process.log", level=logging.INFO) #ログの出力先とレベル

#--デキュースレッドを立てる
def dequeueThread():
    logging.info("start to dequeue")
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
    target = uh.getUnTrackedUser()
    while (len(target) > 0) and (not endReq):
        clawler.update(target[0], 2)
        print("track:" + target[0][1])
        time.sleep(2)
        target = uh.getUnTrackedUser()

    logging.info("complete tracking new users.")
        
initThread = threading.Thread(target=initRecord)
initThread.setDaemon(True)

#--レコード初期化済みのユーザを更新するスレッドを立てる
def updateUser():
    logging.info("start to update tracked user data")
    clawler = Clawler("db/main.db")
    uh = UserHandle()
    target = uh.getNext()
    #--endreqがくるまで止まらない、更新対象がいなくても定期的にDB内に対象ユーザがいないかチェック
    while (not endReq):
        if(len(target) > 0):
            clawler.update(target[0], 0)
            clawler.update(target[0], 1)
            print("update:" + target[0][1] + str(clawler.getAPIStat()))
        time.sleep(2)
        target = uh.getNext()

    if(endReq):
        print("updateUser has received Endreq.")
        logging.info("received endreq")
    else:
        print("complete update tracked users in this phase.")

updateThread = threading.Thread(target=updateUser)
updateThread.setDaemon(True)

#--画像を保存するスレッドを立てる
def saveImages():
    logging.info("save tracked image")

    saver = Saver("db/main.db", "img")
    uh = UserHandle()
    pre_endReq = False #endReqをじかに受け取らない

    #--複数枚持ってきてバイナリ取得
    files = []
    while (not pre_endReq):
        images = uh.getImages(20)
        print("found:" + str(len(images)) + " images.")
        if(len(images) == 0):
            pre_endReq = True

        for image in images:
            #--サーバから取得して待機
            files.append(saver.get(image))
            time.sleep(3)

            #--終了リクエストが来ても'このfor文は'止まらない
            if(endReq):
                pre_endReq = True

    #--適当に名前つけて保存(ここはendReqを無視する)
    saver.save(files)

    if endReq:
        print("saveImages has received EndReq.")
        logging.info("received endreq")
    else:
        print("complete tracked image.")
    return 0

saveThread = threading.Thread(target=saveImages)
saveThread.setDaemon(True)

#--メインスレッドでは15分待つ、これはcronによる自動化のため
initThread.start()
updateThread.start()
saveThread.start()
try:
    n = 12
    time.sleep(n * 60 * 60) #n時間待機
    endReq = True
except KeyboardInterrupt:
    print("終了リクエストを受け取りました。スレッドの終了を待機しています…")
    endReq = True
    initThread.join()
    updateThread.join()
    saveThread.join()
    print("終了リクエストが正常に受理されました。")
    exit(0)