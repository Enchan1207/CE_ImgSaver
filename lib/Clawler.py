#
# DB探索・TLクローリング実行
#

from lib.GetTl import GetTL
from lib.DBQueue import DBQueue
from lib.TweetHandle import TweetHandle
from lib.ErrHandle import ErrHandle
from lib.DBQueue import DBQueue

from datetime import datetime
import time, threading, uuid, logging

class Clawler:
    def __init__(self, dbname):
        self.gt = GetTL()
        self.th = TweetHandle()

        self.identifier = uuid.uuid4()
        self.queue = DBQueue()
        self.queue.initClient(self.identifier)
        self.dbqEvent = threading.Event()

        self.erhd = ErrHandle()

    #--指定ユーザのTLを漁り、DBを更新
    def update(self, user, mode):
        #--何よりも先に、ツイートを漁りきっている/レコード初期化前の場合はreturn
        if(mode == 1 and user[0] != 1):
            return 2

        #--ツイートを取得
        param = {
            "screen_name": user[1],
            "include_entities": True,
            "exclude_replies": False,
            "include_rts": False,
            "count": 100
        }
        #モード分岐 0で最新ツイート 1で過去のツイート 2で指定ユーザのDB初期化
        if(mode == 0):
            param['since_id'] = user[4]
        elif (mode == 1):
            param['max_id'] = user[3]
        
        tlData = self.gt.getTL(param)
        if(tlData['stat'] == 1):
            #--mode=2のときこのエラーが発生した→不正なTwitterIDとみなす
            if(mode == 2):
                self.erhd.addError("Clawler: Invalid Twitter ID: " + user[1])
                self.queue.enQueue(self.identifier, self.dbqEvent, "DELETE FROM userTable WHERE TwitterID=?", (user[1],))
                return 2
            print("API Limitation or Network Error.")
            logging.error("API Limitation or Invalid twitter id")
            return 1

        tweets = tlData['tweets']

        #--ハンドラに渡して解析
        datas = self.th.handle(tweets)

        #--userDBを更新
        if(len(datas) > 0):
            
            #--モードによって更新するIDを変える
            sinceid = user[4]
            lastid = user[3]
            if(mode == 0 or mode == 2): #新規ツイ探索
                sinceid = datas[0]['id'] + 1
            if (mode == 1 or mode == 2): #過去ツイ探索
                lastid = datas[-1]['id'] - 1
            
            #--userDB更新
            sql = "UPDATE userTable SET id=1, modified=?,sinceid=?,lastid=? WHERE TwitterID=?"
            paramtuple = (int(datetime.now().timestamp()), sinceid, lastid, user[1])
            self.queue.enQueue(self.identifier, self.dbqEvent, sql, paramtuple)

            #--imageDB追加
            sql = "INSERT INTO imageTable values(0,?,?,?,?,?)"
            for data in datas:
                #URL抽出
                for mdpath in data['image']:
                    paramtuple = (user[1], data['timestamp'], data['text'], mdpath, "Nodata") #nodataはデータ未取得時の識別子
                    self.queue.enQueue(self.identifier, self.dbqEvent, sql, paramtuple)
                    self.dbqEvent.wait()
                    self.dbqEvent.clear()

            return 0
        else:
            #--ツイートを取得できなくてもmodifiedは変える(これをしないとアカウントが無限ループする)
            sql = "UPDATE userTable SET modified=? WHERE TwitterID=?"
            paramtuple = (int(datetime.now().timestamp()), user[1])
            self.queue.enQueue(self.identifier, self.dbqEvent, sql, paramtuple)

            if(mode == 0):
                logging.info("now no new tweets: " + user[1])
            elif(mode == 1):
                logging.info("all old tweets has clawled: " + user[1])
                sql = "UPDATE userTable SET id=2 WHERE TwitterID=?"
                paramtuple = (user[1],)
                self.queue.enQueue(self.identifier, self.dbqEvent, sql, paramtuple)
            elif(mode == 2):
                logging.error("there is no tweet: " + user[1])
                self.queue.enQueue(self.identifier, self.dbqEvent, "DELETE FROM userTable WHERE TwitterID=?", (user[1],))

            #--DB更新待機
            self.dbqEvent.wait()
            self.dbqEvent.clear()

            return 0


    #--APIの状態を返す
    def getAPIStat(self):
        return self.gt.getAPIStat()