#
# DBのキュー処理
#
from lib.DBAccess import DBAccess
import threading

class DBQueue():
    #--キュー
    rqQueue = [] #リクエスト
    rsQueue = {} #レスポンス

    #--デキューイベント
    dcEvent = threading.Event()
    
    #--
    def connect(self, dbname):
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
            if(len(DBQueue.rqQueue) > 0):
                item = DBQueue.rqQueue.pop(0)
                self.pdo.exec(item['sql'], item['paramtuple'])
                DBQueue.rsQueue[item['client']].append(self.pdo.fetch())
                item['event'].set()
            result = DBQueue.dcEvent.wait(timeout = timeout)
            DBQueue.dcEvent.clear()
            if(result == False):
                print("DBへの接続がタイムアウトしました。")
                break

    #--リザルトキューからフェッチ
    def fetchrst(self, client):
        if(len(DBQueue.rsQueue[client]) > 0):
            return DBQueue.rsQueue[client].pop(0)
        else:
            return []

