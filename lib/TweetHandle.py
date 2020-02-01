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
        rst = {"datalist": [], "info": {"followers": 114514}} #infoで一段挟んでるのは静的なツイート情報が必要になったときの予約

        #--ついでにフォロワー数もとっとく
        if(len(tweets) > 0):
            rst['info']['followers'] = tweets[0]['user']['followers_count']

        for tweet in tweets:
            data = {'id': -1, 'timestamp': -1, 'text': "", 'image': []}
            try:
                entities = tweet['extended_entities']

                #--画像付きツイートの場合はパスとfav数を収集
                if('media' in entities):
                    #--ここで画像に「優先ポイント」を振る
                    data['likes'] = float(tweet['favorite_count']) / float(tweet['user']['followers_count'])
                    # print(str(int(tweet['user']['followers_count'])) + ", " + str(data['likes']))

                    for media in entities['media']:
                        data['image'].append(media['media_url_https'])

                #--ツイートの文字、日時を抽出
                data['id'] = tweet['id']
                data['text'] = tweet['text']
                data['timestamp'] = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y').timestamp()
                rst['datalist'].append(data)

            except KeyError:
                #--ここでは何もしない(キーエラーは「画像のないツイート」に対して実行されるので)
                pass
            except Exception as e:
                logging.error("[TweetHandle(internal)] " + str(e))
        
        return rst