#
# DM送受信管理
#
from lib.config import OAConfig
from requests_oauthlib import OAuth1Session
import json

class DMComm:
    def __init__(self):
        self.url = "https://api.twitter.com/1.1/direct_messages/events/list.json"
        self.twitter = OAuth1Session(OAConfig.CONSUMER_KEY, OAConfig.CONSUMER_SECRET, OAConfig.ACCESS_TOKEN, OAConfig.ACCESS_TOKEN_SECRET)
        self.apistat = {"X-Rate-Limit-Limit": 0, "X-Rate-Limit-Remaining": 0, "X-Rate-Limit-Reset": 0}

    def getEvents(self, param):
        request = self.twitter.get(self.url, params=param)

        #--API状態変数を更新
        for key in self.apistat.keys():
            self.apistat[key] = int(request.headers[key])
        
        return json.loads(request.text)

    def getAPIStat(self):
        return self.apistat