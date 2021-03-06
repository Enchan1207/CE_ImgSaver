# -*- coding: utf-8 -*-
#
# ツイートハンドラ
#

import json
import logging
import traceback
from lib.config import PathConfig
from datetime import datetime


class TweetHandle:
    def __init__(self):
        self.lastid = -1
        self.sinceid = -1

        logging.basicConfig(filename=PathConfig.PATH_LOGOUTPUT,
                            level=logging.INFO)  # ログの出力先とレベル

    # --ツイートを解析してユーザデータおよび画像ファイルのパスを取得
    def handle(self, tweets):
        # infoで一段挟んでるのは静的なツイート情報が必要になったときの予約←今になって効きましたね…
        rst = {"datalist": [], "info": {"followers": -1, "TwitterID":"", "UserName": ""}}

        logs = []

        for tweet in tweets:
            data = {'id': -1, 'timestamp': -1, 'text': "", 'image': []}
            try:
                entities = tweet['extended_entities']

                # --静的なユーザ情報を取得
                rst['info']['followers'] = tweet['user']['followers_count']
                rst['info']['TwitterID'] = tweet['user']['screen_name'];
                rst['info']['UserName'] = tweet['user']['name'];

                # --画像付きツイートの場合はパスとfav数を収集
                if('media' in entities):
                    # --保存画質を設定
                    prioPts = float(tweet['favorite_count']) / float(tweet['user']['followers_count'])
                    followers = tweet['user']['followers_count']
                    quality = self.getQuality(prioPts, followers) # 画質パラメータ(0:skip 1:low 2:high 3:highest)
                    data['likes'] = quality

                    # --URLを追加
                    for media in entities['media']:
                        data['image'].append(media['media_url_https'])

                # --ツイートの文字、日時を抽出
                data['id'] = tweet['id']
                data['text'] = tweet['text']
                data['timestamp'] = datetime.strptime(
                    tweet['created_at'], '%a %b %d %H:%M:%S %z %Y').timestamp()
                rst['datalist'].append(data)

            except KeyError:
                # --ここでは何もしない(キーエラーは「画像のないツイート」に対して実行されるので)
                pass
            except Exception as e:
                logging.error(str(int(datetime.now().timestamp())) +
                              ": [TweetHandle(internal)] " + str(e))
                print(tweets)
                print(traceback.format_exc())

        return rst

    # --保存画質を計算
    def getQuality(self, prioPts, followers):
        quality = 1
        if(prioPts < 0.03):
            if(prioPts >= 0.01):
                quality = 1
            else:
                quality = 0
        else:
            if(followers >= 600):
                if(prioPts >= 0.03 and prioPts <= 0.15):
                    quality = 2
                else:
                    quality = 3
            else:
                if(prioPts >= 0.03 and prioPts <= 0.05):
                    quality = 1
                else:
                    if(prioPts <= 0.2):
                        quality = 2
                    else:
                        quality = 1

        return quality
