#
# DB管理
#

import sqlite3

class DBAccess:

    #--コンストラクタ
    def __init__(self, dbname_):
        self.dbname = dbname_
        self.connection = sqlite3.connect(self.dbname)
        self.cursor = self.connection.cursor()
        
    #--クエリ実行
    def exec(self,sql, paramtuple):
        try:
            self.cursor.execute(sql, paramtuple)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print("error: " + e.args[0])
            return False

    #--フェッチ
    def fetch(self, count = -1):
        if(count < 0):
            return self.cursor.fetchall()
        else:
            return self.cursor.fetchone()


    #--閉じる
    def close(self):
        self.connection.close()
        
    #--デストラクタで一応commitとclose
    def __del__(self):
        self.connection.commit()
        self.connection.close()
    