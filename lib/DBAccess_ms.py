#
# DBAccess(mySQL用)
#

from lib.config import mysqlConfig
from urllib.parse import urlparse
import mysql.connector

class DBAccess_ms:

    dbname = object
    connection = object
    cursor = object

    #--コンストラクタ
    def __init__(self, dbname_):
        try:
            url = urlparse('mysql://'+ mysqlConfig.USERNAME + ":" + mysqlConfig.PASSWORD + '@localhost:3306/' + dbname_)

            DBAccess_ms.connection = mysql.connector.connect(
                host = url.hostname or 'localhost',
                port = url.port or 3306,
                user = url.username or 'root',
                password = url.password or '',
                database = url.path[1:],
            )
            DBAccess_ms.cursor = DBAccess_ms.connection.cursor(dictionary=True, prepared=True)
        except Exception as e:
            print(e)

        return conn.is_connected()

    #--クエリ実行
    def exec(self,sql, paramtuple):
        DBAccess_ms.cursor.execute(sql, [1])
        DBAccess_ms.connection.commit()
    
    #--フェッチ
    def fetch(self, count = 1):
        if(count < 0)
            return DBAccess_ms.cursor.fetchall()
        else:
            return DBAccess_ms.cursor.fetchone()

    #--閉じる
    def close(self):
        DBAccess_ms.connection.close()
        
    #--デストラクタで一応commitとclose
    def __del__(self):
        DBAccess_ms.connection.commit()
        DBAccess_ms.connection.close()
    