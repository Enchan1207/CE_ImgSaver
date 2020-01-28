# -*- coding: utf-8 -*-
#
# DB管理
#

import sqlite3

class DBAccess:

    dbname = object
    connection = object
    cursor = object

    #--コンストラクタ
    def __init__(self, dbname_):
        DBAccess.dbname = dbname_
        DBAccess.connection = sqlite3.connect(DBAccess.dbname)
        DBAccess.cursor = DBAccess.connection.cursor()
        
    #--クエリ実行
    def exec(self,sql, paramtuple):
        try:
            DBAccess.cursor.execute(sql, paramtuple)
            DBAccess.connection.commit()
            return True
        except sqlite3.Error as e:
            return False

    #--フェッチ
    def fetch(self, count = -1):
        if(count < 0):
            return DBAccess.cursor.fetchall()
        else:
            return DBAccess.cursor.fetchone()

    #--閉じる
    def close(self):
        DBAccess.connection.close()
        
    #--デストラクタで一応commitとclose
    def __del__(self):
        DBAccess.connection.commit()
        DBAccess.connection.close()
    