import random
import string
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from werkzeug.security import generate_password_hash, check_password_hash

blacklist = set()

# 加入token黑名单
def add_token_to_blacklist(jwt_payload):
    blacklist.add(jwt_payload['jti'])

# 生成认证码
def generate_identity(id):
    identity = generate_password_hash(id)
    return ''.join(identity)

# 检查认证码
def check_identity(identity, id):
    return check_password_hash(identity, id)

# 生成随机验证码
def generate_verification_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

# 发送邮件
def send_email(recipient,verification_code):
    # 第三方 SMTP 服务
    try:
        # QQ邮箱的SMTP服务器地址
        smtp_server = 'smtp.qq.com'
        smtp_port = 465
        sender_email = 'your_email@qq.com'
        sender_password = 'your_smtp_password'  # QQ邮箱的SMTP授权码

        message = f'【学生服务】你正在使用邮箱验证功能，你的验证码是：{verification_code},有效期5分钟。如非本人操作请忽略'
        subject = '邮箱验证'
        # 创建邮件内容
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['From'] = f"{Header('Sender Name', 'utf-8')} <{sender_email}>"
        msg['To'] = Header(recipient, 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')

        # 连接到SMTP服务器并发送邮件
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [recipient], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
