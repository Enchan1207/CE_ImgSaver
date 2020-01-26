# -*- coding: utf-8 -*-
#
# Twitter画像ダウンローダー
#
from lib.UserHandle import UserHandle
from lib.DBQueue import DBQueue
from lib.Clawler import Clawler
from lib.Saver import Saver
from datetime import datetime
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
        time.sleep(5)
        target = uh.getUnTrackedUser()

    logging.info("complete tracking new users.")

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
            stat = clawler.getAPIStat()
            print("update:" + str(target[0][1]) + " API Status: " + str(stat['remaining']) + "/" + str(stat['limit']))
            time.sleep(3)
        else:
            time.sleep(10)

        target = uh.getNext()

    if(endReq):
        print("updateUser has received(not ACCEPTED) Endreq.")
        logging.info("received endreq")
    else:
        print("complete update tracked users in this phase.")

#--画像を保存するスレッドを立てる
def saveImages():
    logging.info("save tracked image")

    saver = Saver("db/main.db", "img/")
    uh = UserHandle()
    pre_endReq = False #endReqをじかに受け取らない

    #--複数枚持ってきてバイナリ取得
    files = []
    while (not pre_endReq):
        images = uh.getImages(10)
        print("found:" + str(len(images)) + " images.")
        if(len(images) > 0):
            for image in images:
                #--サーバから取得して待機
                files.append(saver.get(image))
                print("get: " + image[4])
                time.sleep(3)

                #--終了リクエストが来ても'このfor文は'止まらない
                if(endReq and (not pre_endReq)):
                    print("saveImages has received(not ACCEPTED) endreq.")
                    pre_endReq = True


            #--適当に名前つけて保存(ここはendReqを無視する)
            print("saveImages has started to save " + str(len(files)) + " images...")
            saver.save(files)
            files = []
        else:
            time.sleep(4)

    if endReq:
        print("saveImages has accepted EndReq.")
        logging.info("accepted endreq")
    else:
        print("complete tracked image.")
    return 0

#--メインスレッドではn時間待つ、これはcronによる自動化のため
updateThread = threading.Thread(target=updateUser)
updateThread.setDaemon(True)
saveThread = threading.Thread(target=saveImages)
saveThread.setDaemon(True)
initThread = threading.Thread(target=initRecord)
initThread.setDaemon(True)

print("--- Start CE_ImgSaver:" + datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')  + "---")
initThread.start()
updateThread.start()
saveThread.start()
try:
    n = 9
    time.sleep(n * 60 * 60) #n時間待機
    endReq = True
except KeyboardInterrupt:
    print("Process end request has requested(not ACCEPTED). please wait other daemon threads...")
    endReq = True
    initThread.join()
    updateThread.join()
    saveThread.join()
    print("End request has accepted.")
    exit(0)