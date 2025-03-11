from flask import Blueprint, request, jsonify,session
from datetime import timedelta
from utils import *
from flask_jwt_extended import jwt_required, get_jwt_identity
from pymongo import MongoClient


common_bp = Blueprint('common', __name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['Student_Dormitory']
dormitory_collection = db['dormitory']
stu_collection = db['student']

#  发送邮件
common_bp.route('/SendEmail', methods=['POST'])
def send_email():
    try:
        data = request.get_json()
        recipient = data['recipient'] # 收件人
        if not recipient:
            raise Exception("错误0:收件人不能为空")
        verification_code = generate_verification_code()
        if not send_email(recipient,verification_code):
            raise Exception("错误1:邮件发送失败")
        session['verification_code'] = verification_code
        session.permanent = True
        common_bp.permanent_session_lifetime = timedelta(minutes=5) # 设置session过期时间
        return jsonify({"message":"邮件发送成功"}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400

# 宿舍总览
@common_bp.route('/allDorm', methods=['POST'])
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

# 查找学生
@common_bp.route('/findStudent', methods=['POST'])
@jwt_required()
def findStudent():
    try:
        current_user = get_jwt_identity()
        account = request.get_json()['account']
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        data = request.get_json()
        DormitoryID = data['DormitoryID']
        BedNumber = data['BedNumber']
        if DormitoryID is None or BedNumber is None:
            raise Exception("参数缺少")
        student_info = stu_collection.find_one({"DormitoryID":DormitoryID,"BedNumber":BedNumber},{'_id':0,'BaseInfo':1})
        if student_info is None:
            raise Exception("错误2:学生不存在")
        StudentName = student_info.get('BaseInfo').get('Name')
        StudentID = student_info.get('BaseInfo').get('StudentID')
        return jsonify({"StudentName":StudentName,"StudentID":StudentID}),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400  

 # 验证验证码
@common_bp.route('/verify_code', methods=['POST'])
def verify_code():
    try:
        data = request.get_json()
        input_code = data.get('verification_code')
        if input_code is None:
            raise Exception('验证码为空')

        stored_code = session.get('verification_code')
        if stored_code is None:
            raise Exception('验证码已过期或不存在')

        if input_code != stored_code:
            raise Exception('验证码错误')
        return jsonify({'message': '验证码验证成功'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400