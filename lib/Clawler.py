#
# DB探索・TLクローリング実行
#

from lib.GetTl import GetTL
from lib.DBAccess import DBAccess
from lib.TweetHandle import TweetHandle
from lib.ErrHandle import ErrHandle

from datetime import datetime

class Clawler:
    def __init__(self, dbname):
        self.gt = GetTL()
        self.th = TweetHandle()
        self.pdo = DBAccess(dbname)
        self.erhd = ErrHandle()

    #--指定ユーザのTLを漁り、DBを更新
    def update(self, user, mode):
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
            param['since_id'] = user[3]
        elif (mode == 1):
            param['max_id'] = user[4]
        
        tlData = self.gt.getTL(param)
        if(tlData['stat'] == 1):
            #--mode=2のときこのエラーが発生した→不正なTwitterIDとみなす
            if(mode == 2):
                self.erhd.addError("Clawler: Invalid Twitter ID: " + user[1])
                self.pdo.exec("DELETE FROM userTable WHERE TwitterID=?", (user[1],))
            print("API Limitation or Network Error.")
            return 1

        tweets = tlData['tweets']

        #--ハンドラに渡して解析
        datas = self.th.handle(tweets)

        #--userDBを更新
        sinceid = datas[0]['id']
        lastid = datas[-1]['id']
        sql = "UPDATE userTable SET id=1, modified=?,lastid=?,sinceid=? WHERE TwitterID=?"
        paramtuple = (int(datetime.now().timestamp()), lastid, sinceid, user[1])
        self.pdo.exec(sql, paramtuple)

        #--imageDBを更新
        sql = "INSERT INTO imageTable values(0,?,?,?,?,?)"
        for data in datas:
            #URL抽出
            for mdpath in data['image']:
                paramtuple = (user[1], data['timestamp'], data['text'], mdpath, "Nodata") #nodataはデータ未取得時の識別子
                self.pdo.exec(sql, paramtuple)

        return 0

    #--APIの状態を返す
    def getAPIStat(self):
        return self.gt.getAPIStat()