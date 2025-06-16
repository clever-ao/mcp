import EmailBox as eb
import pandas as pd
import time
from datetime import datetime
from DetectCharge import DetectCharge
from PageInfo import PageInfo


class DailyEmail:
    def __init__(self, receiver, room_str, local_date):
        self.room_str = room_str
        self.local_date = local_date
        self.email_box = eb.EmailBox(receiver, subject=self.local_date.strftime("%Y年%m月%d日") + " " + self.room_str + " 电费")

    def lowChargeWarning(self, fixed_charge):
        cur_charge = PageInfo(self.room_str, self.local_date).getCurCharge()
        cur_charge = float(cur_charge)
        if cur_charge< fixed_charge:
            self.attachment()
            print(f"发送成功 {cur_charge}")
        else:
            print(f"余额充足 {cur_charge}")

    def attachment(self):
        content = PageInfo(self.room_str, self.local_date).getInfoPage()
        self.email_box.attach_text(content)
        # self.email_box.attach_image("static/logo.png")
        self.email_box.send_email()

    def run(self):
        self.attachment()
