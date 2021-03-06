# -*- coding: utf-8 -*-
#
# DBのキュー処理
#
from lib.DBAccess import DBAccess
from lib.DBAccess_ms import DBAccess_ms
from lib.config import PathConfig
from datetime import datetime
import threading, logging

class DBQueue():
    #--キュー
    rqQueue = [] #リクエスト
    rsQueue = {} #レスポンス

    #--デキューイベント
    dcEvent = threading.Event()

    def __init__(self):
        logging.basicConfig(filename=PathConfig.PATH_LOGOUTPUT, level=logging.INFO) #ログの出力先とレベル
    
    #--
    def connect(self, dbname, usemySQL=False):
        if(usemySQL):
            self.pdo = DBAccess_ms(dbname)
        else:
            self.pdo = DBAccess(dbname)

    #--クライアント初期化
    def initClient(self, client):
        DBQueue.rsQueue[client] = []

    #--エンキュー
    def enQueue(self, client, event, sql, paramtuple=()):
        DBQueue.rqQueue.append({"client": client, "event": event, "sql": sql, "paramtuple": paramtuple})
        DBQueue.dcEvent.set()

    #--デキュー
    def deQueue(self, timeout):
        while True:
            while (len(DBQueue.rqQueue) > 0):
                item = DBQueue.rqQueue.pop(0)
                self.pdo.exec(item['sql'], item['paramtuple'])
                DBQueue.rsQueue[item['client']].append(self.pdo.fetch())
                item['event'].set()

            result = DBQueue.dcEvent.wait(timeout = timeout)
            DBQueue.dcEvent.clear()
            if(result == False):
                logging.error(str(int(datetime.now().timestamp())) + ": [DBQueue] DB Connection time out.")
                break

    #--リザルトキューからフェッチ
    def fetchrst(self, client):
        if(len(DBQueue.rsQueue[client]) > 0):
            return DBQueue.rsQueue[client].pop(0)
        else:
            return []

