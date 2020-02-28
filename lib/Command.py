#
# DMによるコマンド入力を待機する
#
from lib.DMComm import DMComm
from lib.DBQueue import DBQueue
from lib.DBQueue import DBQueue
from lib.config import DMConfig, PathConfig

from datetime import datetime
import time, threading, uuid, logging, re

class Command:
    def __init__(self):
        self.identifier = uuid.uuid4()
        self.queue = DBQueue()
        self.queue.initClient(self.identifier)
        self.dbqEvent = threading.Event()
        self.dc = DMComm()

        logging.basicConfig(filename=PathConfig.PATH_LOGOUTPUT, level=logging.INFO) #ログの出力先とレベル

    #--DMで送られたコマンドを処理する
    def process(self):
        #--API的に大丈夫?
        stat = self.dc.getAPIStat()
        remain = stat['x-rate-limit-remaining']
        if(remain > 3):
            #--イベントからコマンドを収集
            events = self.dc.getEvents(param={"count": 20,})['events']
            commands = [] #処理コマンドキュー
            for event in events:
                #--まずDM送信のイベント?
                if(event['type'] == "message_create"):

                    #--各イベントのデータを収集
                    senderID = event['message_create']['sender_id']
                    cmd = event['message_create']['message_data']['text']

                    #--マスターによって投げられたDMならキューに追加
                    if(senderID == DMConfig.ID_MASTER):
                        commands.append(cmd)
                        logging.debug(str(int(datetime.now().timestamp())) + ": [Command] Added command:" + cmd)

                    #--自分の返信(つまり、コマンドに対するレスポンス)が来た時点でbreak
                    if(re.match(r'\[Responce\]', cmd)):
                        break

            #--コマンドを解析し実行
            resp = "[Responce]"
            for command in commands:
                mc = re.match(r"(add|stat|delete) @(.*)", command)
                if(mc):
                    #--関数と引数に従って実行
                    func = mc.group(1)
                    param = mc.group(2)

                    if(func == "add"):
                        resp += self.add(param)
                        resp += "\n---\n"
                    elif (func == "stat"):
                        resp += self.stat(param)
                        resp += "\n---\n"
                    elif (func == "delete"):
                        resp += self.delete(param)
                        resp += "\n---\n"

            if(not (resp == "[Responce]")):
                self.dc.sendDM(DMConfig.ID_MASTER, resp)
                logging.info(str(int(datetime.now().timestamp())) + ": [Command] The DM Responce was sent.")

            return 0

        else:
            logging.error(str(int(datetime.now().timestamp())) + ": [Command] API Limitation")
            return -1

    #--コマンド:指定ユーザの詳細状態表示
    def stat(self, TwitterID):
        #--ユーザテーブル
        sql = "SELECT * FROM userTable WHERE TwitterID=?"
        paramtuple = (TwitterID,)
        self.queue.enQueue(self.identifier, self.dbqEvent, sql, paramtuple)
        self.dbqEvent.wait()
        self.dbqEvent.clear()
        usrStat = self.queue.fetchrst(self.identifier)

        #--画像テーブル
        sql = "SELECT count(*) FROM imageTable WHERE TwitterID=?"
        self.queue.enQueue(self.identifier, self.dbqEvent, sql, paramtuple)
        self.dbqEvent.wait()
        self.dbqEvent.clear()
        allimg = self.queue.fetchrst(self.identifier)
        sql = "SELECT count(*) FROM imageTable WHERE TwitterID=? AND localPath!=?"
        paramtuple = (TwitterID, "Nodata")
        self.queue.enQueue(self.identifier, self.dbqEvent, sql, paramtuple)
        self.dbqEvent.wait()
        self.dbqEvent.clear()
        svdimg = self.queue.fetchrst(self.identifier)

        #--適当にレスポンス返す
        if(len(usrStat) > 0):
            ids = ["未追跡", "追跡中", "ツイート履歴サーチ済"]
            resp = ""
            resp += "\nTwitterID " + str(TwitterID) + "の詳細:\n"
            resp += "id: " + str(ids[usrStat[0][0]]) + "\n"
            resp += "全体画像枚数: " + str(allimg[0][0]) + "\n"
            resp += "保存済み画像枚数: " + str(svdimg[0][0]) + "\n"
            if(allimg[0][0] > 0):
                resp += "保存率: " + str((float(svdimg[0][0]) / float(allimg[0][0])) * 100.0) + " %\n"
            else:
                resp += "このユーザの画像をトラックできていません"
        else:
            resp = "エラー: twitterid " + str(TwitterID) + " が見つかりません"
        
        return resp

    #--コマンド:指定IDのユーザを追加
    def add(self, TwitterID):
        sql = "INSERT INTO userTable VALUES(0,?,0,0,0,0);"
        paramtuple = (TwitterID,)
        self.queue.enQueue(self.identifier, self.dbqEvent, sql, paramtuple)
        self.dbqEvent.wait()
        self.dbqEvent.clear()
        resp = "\nTwitterID " + str(TwitterID) + "を追加しました。"
        return resp
    
    #--コマンド:指定IDのユーザを削除
    def delete(self, TwitterID):
        sql = "DELETE FROM userTable WHERE TwitterID=?;"
        paramtuple = (TwitterID,)
        self.queue.enQueue(self.identifier, self.dbqEvent, sql, paramtuple)
        self.dbqEvent.wait()
        self.dbqEvent.clear()
        resp = "\nTwitterID " + str(TwitterID) + "を削除しました。"
        return resp