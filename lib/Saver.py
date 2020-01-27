# -*- coding: utf-8 -*-
#
# 画像セーバ
#
import uuid, requests, time, threading, re
from datetime import datetime
from lib.ErrHandle import ErrHandle
from lib.DBQueue import DBQueue

class Saver:
    def __init__(self, dbname, svparent):
        self.queue = DBQueue()
        self.identifier = uuid.uuid4()
        self.queue.initClient(self.identifier)
        self.dqEvent = threading.Event()
        self.svparent = svparent
        self.erhd = ErrHandle()
        self.result = {"require": -1, "found": -1, "successed": -1}

    #--レコードをもとに画像のバイナリを取得
    def get(self, media):
        response = requests.get(media[4])
        imgData = {"url": media[4], "content": response.content}
        response.close()
        return imgData

    #--下からn枚保存
    def save(self, medias):
        try:
            #--保存先を生成してuuid適当につけて保存し、DBを更新
            for imgData in medias:
                name = re.sub(r'^.*\/', "", imgData['url'])
                path = self.svparent + "/" + name
                with open(path, mode = 'wb') as f:
                    f.write(imgData['content'])
                sql = "UPDATE imageTable SET localPath=? WHERE imgPath=?"
                self.queue.enQueue(self.identifier, self.dqEvent, sql, (path, imgData['url']))

                #--DB更新反映待機
                self.dqEvent.wait()
                self.dqEvent.clear()
            return 0

        except Exception as e:
            print(e)
            self.erhd.addError("Saver: " + str(e))
            return 1

    #--保存結果を取得
    def getStat(self):
        return self.result