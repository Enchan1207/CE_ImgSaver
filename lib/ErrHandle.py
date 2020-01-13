#
# エラーハンドル
#

from lib.DBAccess import DBAccess
from datetime import datetime

class ErrHandle:
    def __init__(self):
        self.pdo = DBAccess("db/main.db")

    def addError(self, message):
        self.pdo.exec("INSERT INTO errorTable VALUES(0, ?, ?)", (int(datetime.now().timestamp()), message,))