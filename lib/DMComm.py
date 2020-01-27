#
# DM送受信管理
#
from lib.config import OAConfig
from requests_oauthlib import OAuth1Session
import json

class DMComm:
    def __init__(self):
        self.twitter = OAuth1Session(OAConfig.CONSUMER_KEY, OAConfig.CONSUMER_SECRET, OAConfig.ACCESS_TOKEN, OAConfig.ACCESS_TOKEN_SECRET)
        self.apistat = {"X-Rate-Limit-Limit": 15, "X-Rate-Limit-Remaining": 15, "X-Rate-Limit-Reset": 0}
        self.getEvents(param={"count": 20,})

    #--DM送受信イベントを取得
    def getEvents(self, param):
        #怖いので一応自前チェック
        if(self.getAPIStat()["X-Rate-Limit-Remaining"] > 1):
            url = "https://api.twitter.com/1.1/direct_messages/events/list.json"
            request = self.twitter.get(url, params=param)

            #--API状態変数を更新
            for key in self.apistat.keys():
                self.apistat[key] = int(request.headers[key])
            
            return json.loads(request.text)
        else:
            return json.loads("")

    #--指定したTwitterIDに向けてDMを送信
    def sendDM(self, recID, text):
        #怖いので一応自前チェック
        if(self.getAPIStat()["X-Rate-Limit-Remaining"] > 1):
            url = "https://api.twitter.com/1.1/direct_messages/events/new.json"
            #--POST
            header = {
                "content-type": "application/json"
            }
            param = {
                "event": {
                    "type": "message_create",
                    "message_create":{
                        "target": {
                            "recipient_id": recID
                        },
                        "message_data": {
                            "text": text
                        }
                    }
                }
            }
            request = self.twitter.post(url, headers=header, data=json.dumps(param))

            return json.loads(request.text)
        else:
            return json.loads("")

    #--API状態取得
    def getAPIStat(self):
        return self.apistat