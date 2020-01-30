# -*- coding: utf-8 -*-
#
# ツイートハンドラ
#

import json, logging
from lib.config import PathConfig
from datetime import datetime

class TweetHandle:
    def __init__(self):
        self.lastid = -1
        self.sinceid = -1

        logging.basicConfig(filename=PathConfig.PATH_LOGOUTPUT, level=logging.INFO) #ログの出力先とレベル

    #--ツイートを解析してユーザデータおよび画像ファイルのパスを取得
    def handle(self, tweets):
        datalist = []
        for tweet in tweets:
            data = {'id': -1, 'timestamp': -1, 'text': "", 'image': []}
            try:
                entities = tweet['extended_entities']

                #--画像付きツイートの場合はパスとfav数を収集
                if('media' in entities):
                    data['likes'] = tweet['favorite_count']
                    for media in entities['media']:
                        data['image'].append(media['media_url_https'])

                #--ツイートの文字、日時を抽出
                data['id'] = tweet['id']
                data['text'] = tweet['text']
                data['timestamp'] = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y').timestamp()
                datalist.append(data)

            except KeyError:
                #--ここでは何もしない(キーエラーは「画像のないツイート」に対して実行されるので)
                pass
            except Exception as e:
                logging.error("[TweetHandle(internal)] " + str(e))
        
        return datalist