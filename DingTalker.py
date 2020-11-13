# -*- coding:utf-8 -*-
import time
import json
#import urllib.request
import requests
requests.packages.urllib3.disable_warnings()
import hmac
import hashlib
import base64
from urllib.parse import quote_plus

class DingTalker(object):
    def getSign(self):
        timestamp = int(round(time.time() * 1000))
        secret = 'SEC2587a9f65d52fef3b1bd8e5558ba6ad1ad817c2d969d7a8730cf08f583cd7336'
        #print(bytes(secret,encoding = "utf8"))
        secret_enc = bytes(secret,encoding = "utf8")
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = bytes(string_to_sign,encoding="utf-8")
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = quote_plus(base64.b64encode(hmac_code))
        return [timestamp,sign]

    def getWebHook(self):
        timestamp,sign = self.getSign()
        baseurl='https://oapi.dingtalk.com/robot/send?access_token=a244c910a39a8996d90428528ff8f66419d49b4f9be2bf2562a2d9fedafc10ba'
        finalurl=baseurl + '&timestamp=' + str(timestamp) + '&sign=' + str(sign)
        return finalurl
    
    def getWebHook2(self):
        baseurl='http://172.20.1.120:8060/dingtalk/sales_dingding/send'
        return baseurl

    def sendMsg(self,txtdata):
        url = self.getWebHook()
        header = {
            "Content-Type": "application/json",
            "Charset": "UTF-8"
        }
        data = {
            "msgtype": "text",
            "text": {
                "content": txtdata 
            },
        }

        sendData = json.dumps(data) 
        sendData = sendData.encode("utf-8")  

        f = requests.Session()
	#request = urllib.request.Request(url=url, data=sendData, headers=header, verify=False)
        #opener = urllib.request.urlopen(request)
        get_data = f.post(url,data=sendData,headers=header,verify=False,timeout=30)


    def sendMsg2(self,txtdata):
        url = self.getWebHook2()
        data = {"status":txtdata}
        sendData = json.dumps(data)
        sendData = sendData.encode("utf-8")
        f = requests.Session()
        get_data = f.post(url,data=sendData)


if __name__ == "__main__":
    dt = DingTalker()
    dt.sendMsg2("test msg")
