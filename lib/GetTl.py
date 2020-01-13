#
# タイムライン取得
#

from lib.config import OAConfig
from lib.ErrHandle import ErrHandle

from requests_oauthlib import OAuth1Session
from datetime import datetime
import re
import json

class GetTL:

    def __init__(self):
        self.erhd = ErrHandle()

        self.twitter = OAuth1Session(OAConfig.CONSUMER_KEY, OAConfig.CONSUMER_SECRET, OAConfig.ACCESS_TOKEN, OAConfig.ACCESS_TOKEN_SECRET)
        self.apistat = {"limit": -1, "remaining": -1, "reset": -1}
        self.reloadAPIStat()
        self.remlimit = 100 #残りリクエスト回数がこの数値を切ったらエラーを吐く

    #--paramをもとにツイートを取得
    def getTL(self, param):
        rst = {"stat": 0} #取得結果とステータス

        #--API的にリクエスト投げていい?
        self.reloadAPIStat()
        if(self.apistat['remaining'] <= self.remlimit):
            self.erhd.addError("API count limitation")
            rst['stat'] = 1
            return rst

        #--リクエストを投げ、ヘッダ経由でAPIlimitを更新
        url_ustl = "https://api.twitter.com/1.1/statuses/user_timeline.json"
        request = self.twitter.get(url_ustl, params=param)
        for key in self.apistat.keys():
            #ヘッダ内のキー名とapistatのキー名を一致させる
            hdkey = {"limit" : "X-Rate-Limit-Limit","remaining" : "X-Rate-Limit-Remaining","reset" : "X-Rate-Limit-Reset"}
            self.apistat[key] = int(request.headers[hdkey[key]])
        
        rst['tweets'] = json.loads(request.text)
        return rst

    #--user_timeline APIの状態を更新
    def reloadAPIStat(self):
        try:
            #--rate-limit-statusを呼び出す(このリクエストはAPIレートに影響を受けない)
            apspath = "https://api.twitter.com/1.1/application/rate_limit_status.json"
            param = {"resources":"statuses"}
            request = self.twitter.get(apspath, params=param)
            resp = json.loads(request.text)

            #--API状態変数を更新
            for key in self.apistat.keys():
                self.apistat[key] = int(resp['resources']['statuses']['/statuses/user_timeline'][key])
                
            return 0
        except Exception as e:
            #--DBにエラーログを追加
            self.erhd.addError(str(e))
            return 1

    #--APIの状態をローカルで取得
    def getAPIStat(self):
        #--データを取得した履歴がなければreload
        if(self.apistat['limit'] == -1):
            self.reloadAPIStat()
        return self.apistat