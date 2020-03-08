#
# DBAccess(mySQL用)
#

from lib.config import mysqlConfig
from urllib.parse import urlparse
import mysql.connector
import re

class DBAccess_ms:

    dbname = object
    connection = object
    cursor = object
    stat = False

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
            DBAccess_ms.cursor = DBAccess_ms.connection.cursor(buffered=True)
        except Exception as e:
            pass
            # print(e) #これ許容すると結構うるさい

        DBAccess_ms.stat = DBAccess_ms.connection.is_connected()

    #--クエリ実行
    def exec(self,sql, paramtuple):
        try:
            sql = re.sub(r'\?', '%s', sql)
            if(len(paramtuple) > 0):
                DBAccess_ms.cursor.execute(sql, paramtuple)
            else:
                DBAccess_ms.cursor.execute(sql)
            DBAccess_ms.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False
    
    #--フェッチ
    def fetch(self, count = -1):
        rst=None
        try:
            if(count < 0):
                rst = DBAccess_ms.cursor.fetchall()
            else:
                rst =  DBAccess_ms.cursor.fetchone()
        except mysql.connector.errors.InterfaceError as e:
            pass #ここのエラーはfetchできるデータがないときのエラーなのでつぶす
        except Exception as e:
            print(e, type(e))
        if(rst == None):
            return []
        else:
            return rst

    #--閉じる
    def close(self):
        DBAccess_ms.connection.close()
        
    #--デストラクタで一応commitとclose
    def __del__(self):
        # DBAccess_ms.connection.commit()
        DBAccess_ms.connection.close()
    