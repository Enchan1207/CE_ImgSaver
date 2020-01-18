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
                files.append({"url": media[4], "content": response.content})
                response.close()
                print("GET requests completed. Access waiting...")
                #--複数枚投げられたら3秒待機
                if(len(medias) > 1):
                    time.sleep(3)
                    print("Continue to Save.")

            #--保存先を生成してuuid適当につけて保存し、DBを更新
            for imgData in files:
                path = self.svparent + "/" + str(uuid.uuid4()) + ".jpg"    
                with open(path, mode = 'wb') as f:
                    f.write(imgData['content'])
                sql = "UPDATE imageTable SET localPath=? WHERE imgPath=?"
                self.pdo.exec(sql, (path, imgData['url']))

        except Exception as e:
            print(e)
            self.erhd.addError("Saver: " + str(e))

        result = {
            "found": len(medias),
            "successed": len(files)
        }
        self.result = result
        return result

    #--保存結果を取得
    def getStat(self):
        return self.result
