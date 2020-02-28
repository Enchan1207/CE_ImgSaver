# -*- coding: utf-8 -*-
#
# タイムライン取得
#

from lib.config import OAConfig, PathConfig

from requests_oauthlib import OAuth1Session
from datetime import datetime
import re, json ,logging

class GetTL:

    def __init__(self):
        self.twitter = OAuth1Session(OAConfig.CONSUMER_KEY, OAConfig.CONSUMER_SECRET, OAConfig.ACCESS_TOKEN, OAConfig.ACCESS_TOKEN_SECRET)
        self.apistat = {"limit": -1, "remaining": -1, "reset": -1} #gettl api用のapistat
        self.intAPIStat = {"limit": -1, "remaining": -1, "reset": -1} #apistat更新用のapiのapistat
        self.reloadAPIStat()
        self.remlimit = 100 #残りリクエスト回数がこの数値を切ったらエラーを吐く

        logging.basicConfig(filename=PathConfig.PATH_LOGOUTPUT, level=logging.INFO) #ログの出力先とレベル

    #--paramをもとにツイートを取得
    def getTL(self, param):
        rst = {"stat": 0} #取得結果とステータス

        #--API的にリクエスト投げていい?
        self.getAPIStat()
        if(self.apistat['remaining'] <= self.remlimit):
            if(self.apistat['remaining'] > 0):
                logging.error(str(int(datetime.now().timestamp())) + ": [GetTL] API count limitation")
            else:
                logging.error(str(int(datetime.now().timestamp())) + ": [GetTL] can't get API limit status")
            rst['stat'] = 1
            return rst

        #--リクエストを投げ、ヘッダ経由でAPIstatを更新
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
            #--rate-limit-statusを呼び出す
            apspath = "https://api.twitter.com/1.1/application/rate_limit_status.json"
            request = self.twitter.get(apspath)
            resp = json.loads(request.text)

            #--APIstatを更新
            for key in self.apistat.keys():
                self.intAPIStat[key] = int(resp['resources']['application']['/application/rate_limit_status'][key])
                self.apistat[key] = int(resp['resources']['statuses']['/statuses/user_timeline'][key])
                
            return 0
        except Exception as e:
            logging.error(str(int(datetime.now().timestamp())) + ": [GetTL(internal)] " + str(e))
            return 1

    #--APIの状態をローカルで取得
    def getAPIStat(self):
        #--データを取得した履歴がなければreload
        if(self.apistat['limit'] == -1):
            logging.debug(str(int(datetime.now().timestamp())) + ": [GetTL] Access to API-Limit-list endpoint")
            self.reloadAPIStat()
        return self.apistat