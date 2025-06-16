import json
import re
import time
from datetime import datetime
from Crypto.Cipher import AES
import base64
import requests
from dateutil.relativedelta import relativedelta

ROOT_DOMAIN = "http://10.136.2.5/IBSjnuweb/"


class DetectCharge:
    def __init__(self, acc: str):
        if acc == "":
            raise Exception("账号不能为空")
        self.key = "CetSoftEEMSysWeb"
        self.iv = b"\x19\x34\x57\x72\x90\xAB\xCD\xEF\x12\x64\x14\x78\x90\xAC\xAE\x45"
        self.__check(acc)
        self.__checkOnline()

    @staticmethod
    def getClient() -> requests.Session:
        s = requests.Session()
        header = {
            "Content-Type": "application/json; charset=UTF-8",
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/91.0.4472.77 Safari/537.36",
            "X-Forwarded-For": '127.0.0.1',
        }
        s.headers.update(header)
        return s

    @staticmethod
    def __checkOnline():
        try:
            requests.get(ROOT_DOMAIN, timeout=3)
        except requests.exceptions.ConnectTimeout:
            raise Exception("超时链接，请使用校园网/内网穿透")

    def __getEncrypt(self, text) -> str:
        text = text.replace(" ", "")  # 这里是个大坑
        text = text.replace("|", " ")  # 为了绕过中间的空格进入加密
        BS = 16
        pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
        text = pad(text)
        o_aes = AES.new(self.key.encode(), AES.MODE_CBC, self.iv)
        esb = o_aes.encrypt(text.encode("UTF8"))
        return base64.b64encode(esb).decode("UTF8")

    def __check(self, acc):
        re_right = re.compile(r'^T(\d{5,6})$')
        if not re_right.match(acc):
            raise Exception("宿舍号不符合规则")
        self.acc = acc

    def __generateToken(self):
        timeArray = time.localtime(time.time())
        token_time = time.strftime("%Y-%m-%d | %H:%M:%S", timeArray)
        arr = {
            'userID': self.customerId,
            'tokenTime': token_time,
        }
        return self.__getEncrypt(json.dumps(arr))

    def __getRequestHeader(self):
        timeArray = time.localtime(time.time())
        DateTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        Header = {
            "Token": self.__generateToken(),
            'DateTime': DateTime,
            "Content-Type": "application/json;charset=UTF-8"
        }
        return Header

    def __login(self, paw):
        self.session = self.getClient()
        postUrl = ROOT_DOMAIN + "WebService/JNUService.asmx/Login"
        postData = {"password": paw, "user": self.acc}
        responseRes = self.session.post(postUrl, json=postData)
        response = json.loads(responseRes.text)
        customerId = response['d']['ResultList'][0]['customerId']
        if customerId == 0:
            raise Exception("未能找到该宿舍")
        self.customerId = customerId

    def __getUserInfo(self):
        center_url = ROOT_DOMAIN + "WebService/JNUService.asmx/GetUserInfo"
        header = self.__getRequestHeader()
        responseRes = self.session.post(center_url, headers=header)
        roomInfo = json.loads(responseRes.text)['d']['ResultList'][0]['roomInfo']
        allowanceInfo = json.loads(responseRes.text)['d']['ResultList'][0]['allowanceInfo']
        resultInfo = {
            'balance': roomInfo[1]['keyValue'],
            'subsidies': allowanceInfo[0]['keyValue'],
        }
        return resultInfo

    def __getMonthCharge(self):
        center_url = ROOT_DOMAIN + "WebService/JNUService.asmx/GetCustomerMetricalData"
        header = self.__getRequestHeader()
        cur_month = datetime.now().strftime('%Y-%m')
        next_month = (datetime.now().date() + relativedelta(months=1)).strftime('%Y-%m')
        data = {
            'startDate': f"{cur_month}-01",
            'endDate': f"{next_month}-01",
            'energyType': 0,
            'interval': 1
        }
        responseRes = self.session.post(center_url, headers=header, json=data)
        # chargeList = json.loads(responseRes.text)['d']['ResultList'][0]['datas']
        return responseRes.text

    def run(self, switch):
        try:
            paw = self.__getEncrypt(self.acc)
            self.__login(paw)  # 进行登陆
            if switch == 1:
                return self.__getUserInfo()['balance']  # 拿到信息
            # print(res)  # {'balance': '-122.51', 'subsidies': '0人'}
            elif switch == 2:
                return self.__getMonthCharge()
        except Exception as e:
            print("发生错误", e)
            return "error"

# print(DetectCharge("T110622").run(2))