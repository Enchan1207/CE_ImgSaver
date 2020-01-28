# -*- coding: utf-8 -*-
#
# Twitter画像ダウンローダー
#
from lib.UserHandle import UserHandle
from lib.DBQueue import DBQueue
from lib.Clawler import Clawler
from lib.Saver import Saver
from lib.Command import Command
from lib.config import PathConfig
from datetime import datetime
import time, threading, logging

endReq = False #終了リクエスト
with open(PathConfig.PATH_LOGOUTPUT, "a") as f:
    pass
logging.basicConfig(filename=PathConfig.PATH_LOGOUTPUT, level=logging.INFO) #ログの出力先とレベル

#--デキュースレッドを立てる
def dequeueThread():
    logging.info("[main] start to dequeue")
    queue4Dequeue = DBQueue()
    queue4Dequeue.connect("db/main.db")
    queue4Dequeue.deQueue(120)

dqthread = threading.Thread(target=dequeueThread)
dqthread.setDaemon(True) #デーモンスレッド化しないとタイムアウトするまで終わらなくなる
dqthread.start()

#--未探索のユーザを探索するスレッドを立てる
def initRecord():
    logging.info("[main - InitRecord] start to init untracked user record")
    clawler = Clawler("db/main.db")
    uh = UserHandle()
    target = uh.getUnTrackedUser()
    while (len(target) > 0) and (not endReq):
        clawler.update(target[0], 2)
        logging.info("[main - initRecord] track:" + target[0][1])
        time.sleep(5)
        target = uh.getUnTrackedUser()

    logging.info("[main - initRecord] complete tracking new users.")

#--レコード初期化済みのユーザを更新するスレッドを立てる
def updateUser():
    logging.info("[main - UpdateUser] start to update tracked user data")
    clawler = Clawler("db/main.db")
    uh = UserHandle()
    target = uh.getNext()
    #--endreqがくるまで止まらない、更新対象がいなくても定期的にDB内に対象ユーザがいないかチェック
    while (not endReq):
        if(len(target) > 0):
            clawler.update(target[0], 0)
            clawler.update(target[0], 1)
            stat = clawler.getAPIStat()
            logging.info("[main - updateUser] update:" + str(target[0][1]) + " API Status: " + str(stat['remaining']) + "/" + str(stat['limit']))
            time.sleep(3)
        else:
            time.sleep(10)

        target = uh.getNext()

    if(endReq):
        logging.info("[main - updateUser] received endreq")
    else:
        logging.info("[main - updateUser] complete update")

#--画像を保存するスレッドを立てる
def saveImages():
    logging.info("[main - saveImage] save tracked image")

    saver = Saver("db/main.db", PathConfig.PATH_IMGSAVE)
    uh = UserHandle()
    pre_endReq = False #endReqをじかに受け取らない

    #--複数枚持ってきてバイナリ取得
    files = []
    while (not pre_endReq):
        images = uh.getImages(10)
        logging.info("[main - saveImage] found:" + str(len(images)) + " images.")
        if(len(images) > 0):
            for image in images:
                #--サーバから取得して待機
                files.append(saver.get(image))
                logging.debug("[main - saveImage] get: " + image[4])
                time.sleep(3)

                #--終了リクエストが来ても'このfor文は'止まらない
                if(endReq and (not pre_endReq)):
                    logging.info("[main - saveImage] saveImages has received(not ACCEPTED) endreq.")
                    pre_endReq = True


            #--適当に名前つけて保存(ここはendReqを無視する)
            logging.info("[main - saveImage] started to save " + str(len(files)) + " images...")
            saver.save(files)
            files = []
        else:
            time.sleep(4)

    if endReq:
        logging.info("[main - saveImage] accepted endreq")
    else:
        logging.info("[main - saveImage] complete tracked image.")
    return 0

#--DMを待機するスレッドを立てる
def waitDMEvents():
    while not endReq:
        cmd = Command()
        cmd.process()
        for n in range(80):
            if(endReq):
                break
            time.sleep(1)
    logging.info("[main - waitDMEvents] accepted endReq.")

#--メインスレッドではn時間待つ、これはcronによる自動化のため
updateThread = threading.Thread(target=updateUser)
updateThread.setDaemon(True)
saveThread = threading.Thread(target=saveImages)
saveThread.setDaemon(True)
initThread = threading.Thread(target=initRecord)
initThread.setDaemon(True)
dmThread = threading.Thread(target=waitDMEvents)
dmThread.setDaemon(True)

logging.info("--- Start CE_ImgSaver:" + datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')  + "---")
initThread.start()
updateThread.start()
saveThread.start()
# dmThread.start()
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
    # dmThread.join()
    print("End request has accepted.")
    exit(0)