from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from config import Student
from utils import *

client = MongoClient('mongodb://localhost:27017/')
db = client['Student_Dormitory']
stu_collcetion = db['student']
notice_collcetion = db['notifications']
repair_collection = db['repaires']
dormitory_collection = db['dormitory']

excluded_fields = ['password','_id']
# 创建学生蓝图
stu_bp = Blueprint('stu', __name__)

# 学生登录
@stu_bp.route('/StuLogin', methods=['POST'])
def login():
    data = request.get_json()
    if data is None:
        raise Exception('请求参数错误')
    try:
        stuid = data['stuid']
        password = data['pwd']
        if stuid is None or password is None:
            raise Exception('账号和密码不能为空')
        student = stu_collcetion.find_one({'stuid': stuid})
        if student is not None:
            if check_password_hash(student['password'], password):
                access_token = create_access_token(identity=generate_identity(stuid))
                return jsonify({'message': '登录成功', 'access_token': access_token}), 200
            else:
                raise Exception('密码错误') 
        else:
            raise Exception('用户不存在') 
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400


# 获取个人信息
@stu_bp.route('/StuInfo', methods=['POST'])
@jwt_required()
def get_info():
    current_user = get_jwt_identity()
    data = request.get_json()
    try:   
        stuid = data['stuid']
        if stuid is None:
            raise Exception('学号为空')
        if check_identity(current_user, stuid) == False:
           raise Exception('用户错误') 
        stu = stu_collcetion.find_one({'stuid': stuid},{filed: 0 for filed in excluded_fields})
        if stu is None:
            raise Exception('用户不存在')
        stu_data = {'faculty':stu['faculty'],'name': stu['name'],'stuid': stu['stuid'], 'phone': stu['phone'], 'className': stu['className'], 'dormitoryid': stu['dormitoryid']}
        return jsonify({'message': '获取成功','stu_data':stu_data}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400
    
    
# 修改个人信息
@stu_bp.route('/StuUpdate', methods=['POST'])
@jwt_required()
def update_info():
    try:
        data = request.get_json()
        stuid = data['stuid']
        phone = data['phone']
        className = data['className']
        dormitoryid = data['dormitoryid']
        current_user = get_jwt_identity()
        if check_identity(current_user, stuid) == False:
            raise Exception('当前用户错误') from e
        if stuid is None:
            raise Exception('用户不存在') from e
        stu_collcetion.update_one({'stuid': stuid}, {'$set': { 'phone': phone, 'className': className, 'dormitoryid': dormitoryid}})
        stu = stu_collcetion.find_one({'stuid': stuid},{filed: 0 for filed in excluded_fields})
        stu_data = {'faculty':stu['faculty'],'name': stu['name'], 'stuid': stu['stuid'], 'phone': stu['phone'], 'className': stu['className'], 'dormitoryid': stu['dormitoryid']}
        return jsonify({'message': '修改成功','stu_data':stu_data}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400


# 获取单个通知
@stu_bp.route('/StuNotice', methods=['POST'])
@jwt_required()
def stu_notice():
    try:
        data = request.get_json()
        stuid = data['stuid']
        noticeid = data['noticeid']
        if stuid is None or noticeid is None:
            raise Exception('学号或通知id为空')
        current_user = get_jwt_identity()
        if check_identity(current_user, stuid) == False:
            raise Exception('当前用户错误')
        notice = notice_collcetion.find_one({'noticeid': noticeid},{'_id':0})
        if notice is None:
            raise Exception('当前通知不存在')
        return jsonify({'message': '获取成功','notice':notice}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400


# 获取全部通知
@stu_bp.route('/StuAllNotices', methods=['POST'])
@jwt_required()
def get_notice():
    try:
        data = request.get_json()
        stuid = data['stuid']
        current_user = get_jwt_identity()
        if check_identity(current_user, stuid) == False:
            raise Exception('当前用户错误')
        notices = notice_collcetion.find({},{'_id':0})
        if notices is None:
            return jsonify({'message': '当前无通知'}), 200
        notices_list = []
        for notice in notices:
            notices_list.append(notice)
        return jsonify({'message': '获取成功','notices':notices_list}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400

# 获取单个报修记录
@stu_bp.route('/StuRepair', methods=['POST'])
@jwt_required()
def get_repaire():
    try:
        data  = request.get_json()
        stuid = data['stuid']
        repairid = data['repairid']
        if stuid is None or repairid is None:
            raise Exception('学号或报修id为空')
        current_user = get_jwt_identity()
        if check_identity(current_user, stuid) == False:
            raise Exception('当前用户错误')
        repair = repair_collection.find_one({'repairid': repairid, "stuid": stuid},{'_id':0})
        if repair is None:
            raise Exception('当前报修记录不存在')
        return jsonify({'message': '获取成功','repair':repair}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400

# 获取全部报修记录
@stu_bp.route('/StuRepairs', methods=['POST'])
@jwt_required()
def get_repairs():
    try:
        data = request.get_json()
        stuid = data['stuid']
        current_user = get_jwt_identity()
        if check_identity(current_user, stuid) == False:
            raise Exception('当前用户错误')
        repairs = repair_collection.find({'stuid': stuid},{'_id':0})
        if repairs is None:
            return jsonify({'message': '当前无报修记录'}), 200
        repairs_list = []
        for repair in repairs:
            repairs_list.append(repair)
        return jsonify({'message': '获取成功','repaires':repairs_list}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400

# 宿舍信息
@stu_bp.route('/StuDormitory', methods=['POST'])
@jwt_required()
def get_dormitory():
    try:
        data = request.get_json()
        stuid = data['stuid']
        dormitoryid = data['dormitoryid']
        if stuid is None or dormitoryid is None:
            raise Exception('学号或宿舍id为空')
        current_user = get_jwt_identity()
        if check_identity(current_user, stuid) == False:
            return jsonify({'message': '用户错误'}), 400
        dormitory = dormitory_collection.find_one({'dormitoryid':dormitoryid},{'_id':0})
        if dormitory is None:
            raise Exception('当前宿舍不存在')
        return jsonify({'message': '获取成功','dormitory':dormitory}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400

# 修改密码
@stu_bp.route('/StuChangePwd', methods=['POST'])
@jwt_required()
def change_pwd():
    data = request.get_json()
    stuid = data['stuid']
    phone = data['phone']
    new_password = data['new_password']
    current_user = get_jwt_identity()
    if check_identity(current_user, stuid) == False:
        return jsonify({'message':'当前用户错误'}), 400
    stu = stu_collcetion.find_one({'stuid':stuid},{'_id':0})
    if stu is not None:
        pass
    else:
        return jsonify({'message':'用户不存在'}), 400