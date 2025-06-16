import smtplib
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import time


class EmailBox:
    def __init__(self, receiver, date=time.strftime("%Y-%m-%d", time.localtime()), subject="测试邮件"):
        self.smtp_server = "smtp.163.com"  # 邮箱服务器
        self.sender = "qq2895967878@163.com"  # 发邮件的人
        self.password = "HWQAGVJYTMMLDLMV"  # 授权码
        self.receiver = receiver
        self.subject = subject
        self.msg = None
        self.init_msg(date)
        self.image_id = 0

    def init_msg(self, date):
        self.msg = MIMEMultipart('mixed')
        self.msg['Subject'] = self.subject
        self.msg['From'] = self.sender
        self.msg['TO'] = ";".join(self.receiver)
        self.msg['Date'] = date

    def attach_text(self, text):
        html = MIMEText(text, 'html', 'utf-8')
        self.msg.attach(html)

    def attach_file(self, file_path):
        # 构造附件
        send_file = open(f'{file_path}', 'rb').read()
        text_att = MIMEApplication(send_file)
        text_att["Content-Type"] = 'application/octet-stream'
        # 重命名附件文件
        text_att.add_header('Content-Disposition', 'attachment',
                            filename=f'')
        self.msg.attach(text_att)

    def attach_image(self, image_path):
        send_image = open(f'{image_path}', 'rb').read()  # 打开文件，可以使用相对路劲和绝对路径
        image = MIMEImage(send_image)
        image.add_header('Content-ID', f'<image0>')
        # image["Content-Disposition"] = f'attachment; filename="{self.image_id}.png"'
        self.image_id += 1
        self.msg.attach(image)

    def send_email(self):
        try:
            s = smtplib.SMTP()
            s.connect(self.smtp_server, 25)
            s.login(self.sender, self.password)
            s.sendmail(self.sender, self.receiver, self.msg.as_string())
            s.quit()
        except Exception as e:
            print(e)
