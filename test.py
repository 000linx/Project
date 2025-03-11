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


# 测试接口，jwt与principal权限测试
@test_bp.route('/test', methods=['POST'])
def test():
    try:
        current_user = get_jwt_identity()
        account = request.get_json()['account']
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        return jsonify({'message':'测试成功'}),200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400