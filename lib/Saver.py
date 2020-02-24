# -*- coding: utf-8 -*-
#
# 画像セーバ
#
import uuid
import requests
import time
import threading
import re
import os
import logging
import io
from datetime import datetime
from lib.DBQueue import DBQueue
from lib.config import PathConfig
from PIL import Image


class Saver:
    def __init__(self, dbname, svparent):
        self.queue = DBQueue()
        self.identifier = uuid.uuid4()
        self.queue.initClient(self.identifier)
        self.dqEvent = threading.Event()
        self.svparent = svparent
        self.result = {"require": -1, "found": -1, "successed": -1}

        logging.basicConfig(filename=PathConfig.PATH_LOGOUTPUT,
                            level=logging.INFO)  # ログの出力先とレベル

    # --レコードをもとに画像のバイナリを取得
    def get(self, media):
        # --優先ポイント取得+URLパース
        quality = media[2]
        urlRaw = media[5]
        url = urlRaw
        urlElem = re.search(r'(.*\/)(.*?).(jpg|png)$', urlRaw).groups()
        urlPath = urlElem[0]
        urlID = urlElem[1]
        urlSuffix = urlElem[2]
        isMediathumb = bool(re.match(r'ext_tw_video_thumb', urlRaw))

        # --動画のサムネは高画質URLに対応していないので弾く
        if not isMediathumb:
            if(quality >= 2):  # 高画質
                url = urlPath + urlID + "?format=png"
            if(quality == 3):  # 最高画質
                url += "&name=4096x4096"

        response = requests.get(url)

        imgData = {"url": urlRaw,"content": response.content}
        response.close()
        return imgData

    # --下からn枚保存
    def save(self, medias):
        try:
            # --適当に保存し、DBを更新
            for imgData in medias:
                # --フィルタされた画像のパスとサムネイルのパス
                name = re.sub(r'^.*\/', "", imgData['url'])
                originPath = self.svparent + "/" + name
                thumbPath = self.svparent + "/thumb_" + name
                if(not os.path.exists(originPath)):
                    if(len(imgData['content']) > 0):
                        # --オリジナル保存
                        with open(originPath, mode='wb') as f:
                            f.write(imgData['content'])

                        # --サムネイル作成+保存
                        pilImage = Image.open(io.BytesIO(imgData['content']))
                        img_resize = pilImage.resize((200, int(pilImage.height * (200 / pilImage.width))), Image.NEAREST)
                        img_resize.save(thumbPath)
                    else:
                        logging.info(
                            "[Saver] this image has no data: " + str(imgData['url']))
                else:
                    logging.info(
                        "[Saver] this image is already saved: " + str(originPath))

                sql = "UPDATE imageTable SET localPath=? WHERE imgPath=?"
                self.queue.enQueue(self.identifier, self.dqEvent,
                                   sql, (originPath, imgData['url']))

                # --DB更新反映待機
                self.dqEvent.wait()
                self.dqEvent.clear()
            return 0

        except Exception as e:
            logging.error("[Saver(internal)] " + str(e))
            return 1

    # --保存結果を取得
    def getStat(self):
        return self.result
