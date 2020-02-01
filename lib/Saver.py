# -*- coding: utf-8 -*-
#
# 画像セーバ
#
import uuid, requests, time, threading, re, os, logging
from datetime import datetime
from lib.DBQueue import DBQueue
from lib.config import PathConfig

class Saver:
    def __init__(self, dbname, svparent):
        self.queue = DBQueue()
        self.identifier = uuid.uuid4()
        self.queue.initClient(self.identifier)
        self.dqEvent = threading.Event()
        self.svparent = svparent
        self.result = {"require": -1, "found": -1, "successed": -1}

        logging.basicConfig(filename=PathConfig.PATH_LOGOUTPUT, level=logging.INFO) #ログの出力先とレベル

    #--レコードをもとに画像のバイナリを取得
    def get(self, media):
        #--優先ポイント取得+URLパース
        likes = media[2]
        url_raw = media[5]
        url = url_raw
        url_elem = re.search(r'(.*\/)(.*?).(jpg|png)$', url_raw).groups(0)
        url_path = url_elem[0]
        url_id = url_elem[1]
        url_sf = url_elem[2]

        if(likes >= 0.3): #高画質
            url = url_path + url_id + "?format=png"
        if(likes >= 0.8): #最高画質
            url = url_path + url_id + "?format=png&name=4096x4096"

        response = requests.get(url)
        imgData = {"url": url, "content": response.content}
        response.close()
        return imgData

    #--下からn枚保存
    def save(self, medias):
        try:
            #--保存先を生成してuuid適当につけて保存し、DBを更新
            for imgData in medias:
                name = re.sub(r'^.*\/', "", imgData['url'])
                path = self.svparent + "/" + name
                if(not os.path.exists(path)):
                    with open(path, mode = 'wb') as f:
                        f.write(imgData['content'])
                else:
                    logging.info("[Saver] this image is already saved: " + str(path))

            sql = "UPDATE imageTable SET localPath=? WHERE imgPath=?"
            self.queue.enQueue(self.identifier, self.dqEvent, sql, (path, imgData['url']))

            #--DB更新反映待機
            self.dqEvent.wait()
            self.dqEvent.clear()
            return 0

        except Exception as e:
            logging.error("[Saver(internal)] " + str(e))
            return 1

    #--保存結果を取得
    def getStat(self):
        return self.result