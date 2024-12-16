from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from utils import *

client = MongoClient('mongodb://localhost:27017/')
db = client['Student_Dormitory']
admin_collection = db['admin']

# 创建管理员蓝图
admin_bp = Blueprint('admin', __name__)



# 管理员登录
@admin_bp.route('/adminLogin', methods=['POST'])
def login():
    data = request.get_json()
    teacherid = data['teacherid']
    password = data['password']
    admin = admin_collection.find_one({'username': teacherid})
    if admin is not None:
        if check_password_hash(admin['password'],password):
            access_token = create_access_token(indentity = generate_identity(teacherid))
            return jsonify({'message':'登录成功','access_token':access_token}),200
        else:
            return jsonify({'message':'密码错误'}),400
    else:
        return jsonify({'message':'用户名错误'}),400
    
# 修改管理信息
@admin_bp.route('/adminUpdate', methods=['POST'])
def admin_update():
    data = request.get_json()
    