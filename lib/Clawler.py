# -*- coding: utf-8 -*-
#
# DB探索・TLクローリング実行
#

from lib.GetTl import GetTL
from lib.DBQueue import DBQueue
from lib.TweetHandle import TweetHandle
from lib.DBQueue import DBQueue
from lib.config import PathConfig

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

        logging.basicConfig(filename=PathConfig.PATH_LOGOUTPUT, level=logging.INFO) #ログの出力先とレベル

    #--指定ユーザのTLを漁り、DBを更新
    def update(self, user, mode):
        #--何よりも先に、ツイートを漁りきっている/レコード初期化前の場合はreturn
        if(mode == 1 and user[0] != 1):
            return 2
            
        #--ツイートを取得
        param = {
            "user_id": user[1],
            "include_entities": True,
            "exclude_replies": False,
            "include_rts": False,
            "count": 200
        }
        #モード分岐 0で最新ツイート 1で過去のツイート 2で指定ユーザのDB初期化
        if(mode == 0):
            param['since_id'] = user[4]
        elif (mode == 1):
            param['max_id'] = user[3]
        
        tlData = self.gt.getTL(param)

        if(not ('tweets' in tlData)):
            logging.error(str(int(datetime.now().timestamp())) + ": [Clawler] Fatal Error: can't get tweet timeline.")
            return 1

        #--ツイート取得時にエラー発生
        if('errors' in tlData['tweets']):
            #--mode=2のときこのエラーが発生した→不正なuserIDとみなす
            logging.error(str(int(datetime.now().timestamp())) + ": [Clawler] Can't get Tweets: " + str(user[1]))
            if(mode == 2):
                self.queue.enQueue(self.identifier, self.dbqEvent, "DELETE FROM userTable WHERE userID=?", (user[1],))
                return 2

        #--API制限に引っかかった
        if(tlData['stat'] == 1):
            logging.error(str(int(datetime.now().timestamp())) + ": [Clawler] API Limitation")
            return 1

        tweets = tlData['tweets']

        #--ハンドラに渡して解析
        result = self.th.handle(tweets)
        datas = result['datalist']

        #--ツイートを取得できたらlastidとsinceidを更新
        if(len(tweets) > 0):
            sinceid = user[4]
            lastid = user[3]
            if(mode == 0 or mode == 2): #新規ツイ探索
                sinceid = tweets[0]['id'] + 1
            if (mode == 1 or mode == 2): #過去ツイ探索
                lastid = tweets[-1]['id'] - 1

            #--userDB更新
            sql = "UPDATE userTable SET id=1, modified=?,sinceid=?,lastid=? WHERE userID=?"
            paramtuple = (int(datetime.now().timestamp()), sinceid, lastid, user[1])
            self.queue.enQueue(self.identifier, self.dbqEvent, sql, paramtuple)
            
            #--フォロワー数とTwitterIDを設定
            sql = "UPDATE userTable SET followers=?,TwitterID=?,AccountName=? WHERE userID=?"
            paramtuple = (result['info']['followers'], result['info']['TwitterID'], result['info']['UserName'], user[1])
            self.queue.enQueue(self.identifier, self.dbqEvent, sql, paramtuple)

            self.dbqEvent.wait()
            self.dbqEvent.clear()

            #--さらにメディアツイートも含まれていた場合は、imageTableにinsertする
            if(len(datas) > 0):
                #--imageDB追加
                sql = "INSERT INTO imageTable values(0,?,?,?,?,?,?)"
                for data in datas:
                    #URL抽出
                    for mdpath in data['image']:
                        paramtuple = (user[1], data['likes'], data['timestamp'], data['text'], mdpath, "Nodata") #nodataはデータ未取得時の識別子
                        self.queue.enQueue(self.identifier, self.dbqEvent, sql, paramtuple)
                        self.dbqEvent.wait()
                        self.dbqEvent.clear()

        else:
            # 新規ツイートがない/全てのツイートをクローリングした/ツイートそのものをクローリングできなかった
            if(mode == 0):
                logging.debug(str(int(datetime.now().timestamp())) + ": [Clawler] now no new tweets: " + user[1])
            elif(mode == 1):
                logging.info(str(int(datetime.now().timestamp())) + ": [Clawler] all old tweets has clawled: " + user[1])
                sql = "UPDATE userTable SET id=2 WHERE userID=?"
                paramtuple = (user[1],)
                self.queue.enQueue(self.identifier, self.dbqEvent, sql, paramtuple)
            elif(mode == 2):
                logging.info(str(int(datetime.now().timestamp())) + ": [Clawler] there is no tweet: " + user[1])
                self.queue.enQueue(self.identifier, self.dbqEvent, "DELETE FROM userTable WHERE userID=?", (user[1],))

            if(mode>0):
                #--DB更新待機
                self.dbqEvent.wait()
                self.dbqEvent.clear()

        #--modifiedは必ず更新(これをしないとアカウントが無限ループする)
        sql = "UPDATE userTable SET modified=? WHERE userID=?"
        paramtuple = (int(datetime.now().timestamp()), user[1])
        self.queue.enQueue(self.identifier, self.dbqEvent, sql, paramtuple)

        #--DB更新待機
        self.dbqEvent.wait()
        self.dbqEvent.clear()

        return 0


    #--APIの状態を返す
    def getAPIStat(self):
        return self.gt.getAPIStat()