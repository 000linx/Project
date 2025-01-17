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
    try:
        data = request.get_json()
        
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400

    