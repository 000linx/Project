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
        return jsonify({'message': '请求参数出错'}), 400
    try:
        stuid = data['stuid']
        password = data['pwd']
        student = stu_collcetion.find_one({'stuid': stuid})
        print(student)
        if student is not None:
            if check_password_hash(student['password'], password):
                access_token = create_access_token(identity=generate_identity(stuid))

                return jsonify({'message': '登录成功', 'access_token': access_token}), 200
            else:
                return jsonify({'message': '密码错误'}), 400
        else:
            return jsonify({'message': '当前学生不存在'}), 400
    except Exception as e:
        return jsonify({'message': '登录异常'}), 400

# 获取个人信息
@stu_bp.route('/StuInfo', methods=['POST'])
@jwt_required()
def get_info():
    current_user = get_jwt_identity()
    data = request.get_json()
    try:   
        stuid = data['stuid']
        if check_identity(current_user, stuid) == False:
            return jsonify({'message': '用户错误'}), 400
        stu = stu_collcetion.find_one({'stuid': stuid},{filed: 0 for filed in excluded_fields})
        if stu is None:
            return jsonify({'message': '当前用户不存在'}), 400
        stu_data = {'faculty':stu['faculty'],'name': stu['name'],'stuid': stu['stuid'], 'phone': stu['phone'], 'className': stu['className'], 'dormitoryid': stu['dormitoryid']}
        stu_bp.logger.info(f'用户{stuid}获取个人信息成功')
        return jsonify({'message': '获取成功','stu_data':stu_data}), 200
    except Exception as e:
        stu_bp.logger.error(e)
        return jsonify({'message': '获取异常'}), 400

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
    



# 修改个人信息
@stu_bp.route('/StuUpdate', methods=['POST'])
@jwt_required()
def update_info():
    data = request.get_json()
    stuid = data['stuid']
    phone = data['phone']
    className = data['className']
    dormitoryid = data['dormitoryid']
    current_user = get_jwt_identity()
    if check_identity(current_user, stuid) == False:
        return jsonify({'message': '用户错误'}), 400
    if stuid is None:
        return jsonify({'message': '当前用户不存在'}), 400
    stu_collcetion.update_one({'stuid': stuid}, {'$set': { 'phone': phone, 'className': className, 'dormitoryid': dormitoryid}})
    stu = stu_collcetion.find_one({'stuid': stuid},{filed: 0 for filed in excluded_fields})
    stu_data = {'faculty':stu['faculty'],'name': stu['name'], 'stuid': stu['stuid'], 'phone': stu['phone'], 'className': stu['className'], 'dormitoryid': stu['dormitoryid']}
    return jsonify({'message': '修改成功','stu_data':stu_data}), 200

# 获取单个通知
@stu_bp.route('/StuNotice', methods=['POST'])
@jwt_required()
def stu_notice():
    data = request.get_json()
    noticeid = data['noticeid']
    notice = notice_collcetion.find_one({'noticeid': noticeid},{'_id':0})
    if notice is None:
        return jsonify({'message': '当前通知不存在'}), 400
    return jsonify({'message': '获取成功','notice':notice}), 200

# 获取全部通知
@stu_bp.route('/StuNotices', methods=['GET'])
@jwt_required()
def get_notice():
    notices = notice_collcetion.find({},{'_id':0})
    notice_list = []
    for notice in notices:
        notice_list.append(notice)
    return jsonify({'message': '获取成功','notice_list':notice_list}), 200

# 获取单个报修记录
@stu_bp.route('/StuRepaire', methods=['POST'])
@jwt_required()
def get_repaire():
    data = request.get_json()
    stuid = data['stuid']
    current_user = get_jwt_identity()
    if check_identity(current_user, stuid) == False:
        return jsonify({'message': '用户错误'}), 400
    repairid = data['repairid']
    repair = repair_collection.find_one({'stuid': stuid, 'repairid': repairid},{'_id':0})
    if repair is None:
        return jsonify({'message': '当前报修记录不存在'}), 400
    return jsonify({'message': '获取成功','repair':repair}), 200

# 获取全部报修记录
@stu_bp.route('/StuRepaires', methods=['POST'])
@jwt_required()
def get_repairs():
    data = request.get_json()
    stuid = data['stuid']
    current_user = get_jwt_identity()
    if check_identity(current_user, stuid) == False:
        return jsonify({'message': '用户错误'}), 400
    repairs = repair_collection.find({'stuid': stuid},{'_id':0})
    repairs_list = []
    for repair in repairs:
        repairs_list.append(repair)
    return jsonify({'message': '获取成功',"repairs":repairs_list}), 200

# 宿舍信息
@stu_bp.route('/StuDormitory', methods=['POST'])
@jwt_required()
def get_dormitory():
    data = request.get_json()
    stuid = data['stuid']
    dormitoryid = data['dormitoryid']
    current_user = get_jwt_identity()
    if check_identity(current_user, stuid) == False:
        return jsonify({'message': '用户错误'}), 400
    dormitory = dormitory_collection.find_one({'dormitoryid':dormitoryid},{'_id':0})
    if dormitory is None:
        return jsonify({'message': '当前宿舍不存在'}), 400
    return jsonify({'message': '获取成功','dormitory':dormitory}), 200
