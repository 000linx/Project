from utils import *
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import get_jwt_identity,create_access_token, jwt_required
from flask_principal import Principal,Identity,generate_identity,check_identity,Permission,RoleNeed

test_bp = Blueprint('test', __name__)
# 创建权限管理对象
principals = Principal(test_bp)

# 创建admin角色
admin_permission = Permission(RoleNeed('admin'))
# 创建user角色
user_permission = Permission(RoleNeed('user'))

stuid = "202202060222"


@test_bp.route('/TestLogin', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if data is None:
            raise Exception('错误0:请求参数为空')
        username = data.get('username')
        password = data.get('password')
        if username is None or password is None:
            raise Exception('错误1:账号或密码为空')
        if username == 'admin' and password == 'admin':
            identity = Identity(username)
            identity.provides.add(RoleNeed('admin'))
            principals.set_identity(identity)
            access_token = create_access_token(identity=generate_identity(username))
            return jsonify({'message': '登录成功', 'access_token': access_token}), 200
        else:
            raise Exception('错误2:账号或密码错误')
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400



@test_bp.route('/TestInfo', methods=['POST'])
@jwt_required()
@admin_permission.require()
def get_info():
    try:
        data = request.get_json()
        if data is None:
            raise Exception('错误0:请求参数为空')
        username = data.get('username')
        current_user = get_jwt_identity()
        if check_identity(current_user, username) == False:
            raise Exception('错误1:用户错误')
        return jsonify({'message': '获取成功','stu_data':username}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400


@test_bp.route('/send_email', methods=['POST'])
def send_email():
    try:
        data = request.get_json()
        if data is None:
            raise Exception('错误0:请求参数为空')
        recipient = data.get('recipient')
        subject = data.get('subject')
        message = data.get('message')
        if recipient is None or subject is None or message is None:
            raise Exception('错误1:收件人、主题或内容为空')

        # QQ邮箱的SMTP服务器地址
        smtp_server = 'smtp.qq.com'
        smtp_port = 465 
        sender_email = 'your_email@qq.com'
        sender_password = 'your_smtp_password'  # QQ邮箱的SMTP授权码

        # 创建邮件内容
        msg = MIMEText(message, 'plain', 'utf-8')
        message['From'] = f"{Header('Sender Name', 'utf-8')} <{sender_email}>"
        msg['To'] = Header(recipient)
        msg['Subject'] = Header(subject, 'utf-8')

        # 连接到SMTP服务器并发送邮件
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [recipient], msg.as_string())
        server.quit()

        return jsonify({'message': '邮件发送成功'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
