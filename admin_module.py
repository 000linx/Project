from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity,get_jwt
from werkzeug.security import check_password_hash
from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from utils import *
from collections import namedtuple

client = MongoClient('mongodb://localhost:27017/')
db = client['Student_Dormitory']
admin_collection = db['admin']
dormitory_collection = db['dormitory']
excluded_fields = ['password','_id']

# 创建管理员蓝图
admin_bp = Blueprint('admin', __name__)


# 管理员登录
@admin_bp.route('/adminLogin', methods=['POST'])
def login():
    try:
        data = request.get_json()
        account = data['account']
        password = data['password']
        if account is None or password is None:
            raise Exception("错误0:账户或密码为空")
        admin = admin_collection.find_one({'account':account})
        if admin is None:
            raise Exception("错误1:用户不存在")
        if not check_password_hash(admin['password'],password):
            raise Exception("错误2:密码错误")
        access_token = create_access_token(identity=generate_identity(account))
        return jsonify({'messange':'登录成功','access_token':access_token}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400
    
# 退出登录
@admin_bp.route('/adminLogout', methods=['POST'])
@jwt_required()
def logout():
    account = request.get_json()['account']
    current_user = get_jwt_identity()
    try:
        if account is None:
            raise Exception("错误0:账户为空")
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        add_token_to_blacklist(get_jwt())
        return jsonify({'message': '退出成功'}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}),400

# 宿舍总览
@admin_bp.route('/allDorm', methods=['POST'])
@jwt_required()
def view():
    try:
        current_user = get_jwt_identity()
        account = request.get_json()['account']
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        dorms = dormitory_collection.find({},{'_id':0})
        dorms_list = list(dorms)
        return jsonify(dorms_list),200        
    except Exception as e:
        return jsonify("发生异常",str(e)),400    
    

# 管理员信息
@admin_bp.route('/adminInfo', methods=['POST'])
@jwt_required()
def adminInfo():
    try:
        current_user = get_jwt_identity()
        account = request.get_json()['account']
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        admin = admin_collection.find_one({'account':account},{'_id':0})
        return jsonify(admin),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400


# 维修申请
