#
# 画像セーバ
#
import uuid
import requests
import time

from lib.ErrHandle import ErrHandle
from lib.DBAccess import DBAccess

class Saver:
    def __init__(self, dbname, svparent):
        self.pdo = DBAccess(dbname)
        self.svparent = svparent
        self.erhd = ErrHandle()
        self.result = {"require": -1, "found": -1, "successed": -1}

    #--下からn枚保存
    def save(self, medias):
        try:
            #--各URLに合わせてHTTPReq、とりあえずリストアップ
            files = []
            for media in medias:
                response = requests.get(media[4])
                files.append(response.content)
                response.close()
                print("GET requests completed. Access waiting...")
                time.sleep(5)
                print("Continue to Save.")

            #--保存先を生成してuuid適当につけて保存し、DBを更新
            for imgData in files:
                path = self.svparent + "/" + str(uuid.uuid4()) + ".jpg"    
                with open(path, mode = 'wb') as f:
                    f.write(imgData)
                sql = "UPDATE imageTable SET localPath=?"
                self.pdo.exec(sql, (path,))

        except Exception as e:
            print(e)
            self.erhd.addError("Saver: " + str(e))

        result = {
            "found": len(medias),
            "successed": len(files)
        }
        self.result = result

    #--保存結果を取得
    def getStat(self):
        return self.result
