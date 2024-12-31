from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask import Blueprint, request, jsonify,session
from werkzeug.security import check_password_hash
from pymongo import MongoClient
from datetime import timedelta
from utils import *

blacklist = set()

# 数据库配置以及连接
client = MongoClient('mongodb://localhost:27017/')
db = client['Student_Dormitory']
stu_collection = db['student']
notice_collection = db['notifications']
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
        raise Exception('错误0:请求参数为空')
    try:
        StudentID = data['StudentID']
        password = data['password']
        if StudentID is None or password is None:
            raise Exception('错误1:账号或密码为空')
        student = stu_collection.find_one({ "StudentID": StudentID })
        if student is not None:
            if check_password_hash(student['password'], password):
                access_token = create_access_token(identity=generate_identity(StudentID))
                return jsonify({'message': '登录成功', 'access_token': access_token}), 200
            else:
                raise Exception('错误2:密码错误') 
        else:
            raise Exception('错误3:用户不存在') 
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400
    
# 退出登录
@stu_bp.route('/StuLogout', methods=['POST'])
@jwt_required()
def logout():
    StudentID = request.get_json()['StudentID']
    current_user = get_jwt_identity()
    try:
        if StudentID is None:
            raise Exception('错误0:学号为空')
        if check_identity(current_user,StudentID) == False:
            raise Exception('错误1:用户错误')
        add_token_to_blacklist(get_jwt())
        return jsonify({'message': '退出成功'}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400

#####################################################################################################
# 学生信息
# 获取个人信息
@stu_bp.route('/StuInfo', methods=['POST'])
@jwt_required()
def get_info():
    current_user = get_jwt_identity()
    data = request.get_json()
    try:   
        StudentID = data['StudentID']
        if StudentID is None:
            raise Exception('错误0:学号为空')
        if check_identity(current_user, StudentID) == False:
           raise Exception('错误1:用户错误') 
        stu = stu_collection.find_one({'StudentID': StudentID},{filed: 0 for filed in excluded_fields})
        if stu is None:
            raise Exception('错误2:用户不存在')
        return jsonify({'message': '获取成功','stu_data':stu}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400
    
    
# 修改个人信息
@stu_bp.route('/StuUpdateInfo', methods=['POST'])
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
        stu_collection.update_one({'stuid': stuid}, {'$set': { 'phone': phone, 'className': className, 'dormitoryid': dormitoryid}})
        stu = stu_collection.find_one({'stuid': stuid},{filed: 0 for filed in excluded_fields})
        stu_data = {'faculty':stu['faculty'],'name': stu['name'], 'stuid': stu['stuid'], 'phone': stu['phone'], 'className': stu['className'], 'dormitoryid': stu['dormitoryid']}
        return jsonify({'message': '修改成功','stu_data':stu_data}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400

#####################################################################################################
# 通知信息
# 获取单个通知
@stu_bp.route('/StuNotice', methods=['POST'])
@jwt_required()
def stu_notice():
    try:
        data = request.get_json()
        StudentID = data['StudentID']
        noticeid = data['noticeid']
        if StudentID is None or noticeid is None:
            raise Exception('错误0:学号或通知id为空')
        current_user = get_jwt_identity()
        if check_identity(current_user, StudentID) == False:
            raise Exception('错误1:当前用户错误')
        notice = notice_collection.find_one({'noticeid': noticeid},{'_id':0})
        if notice is None:
            raise Exception('错误2:当前通知不存在')
        return jsonify({'message': '获取成功','notice':notice}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400


# 获取全部通知
@stu_bp.route('/StuAllNotices', methods=['POST'])
@jwt_required()
def get_notice():
    try:
        data = request.get_json()
        StudentID = data['StudentID']
        current_user = get_jwt_identity()
        if check_identity(current_user, StudentID) == False:
            raise Exception('错误0:当前用户错误')
        notices = notice_collection.find({},{'_id':0})
        if notices is None:
            return jsonify({'message': '当前通知为空'}), 200
        notices_list = []
        for notice in notices:
            notices_list.append(notice)
        return jsonify({'message': '获取成功','notices':notices_list}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400

#####################################################################################################
# 报修信息
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

#####################################################################################################
# 宿舍信息
# 获取宿舍信息
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


#####################################################################################################
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
    stu = stu_collection.find_one({'stuid':stuid},{'_id':0})
    if stu is not None:
        pass
    else:
        return jsonify({'message':'用户不存在'}), 400
    

# 发送邮件
@stu_bp.route('/StuSendEmail', methods=['POST'])
@jwt_required()
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
        verification_code = generate_verification_code()
        session['verification_code'] = verification_code
        session.permanent = True
        stu_bp.permanent_session_lifetime = timedelta(minutes=5)
        if send_email(recipient,verification_code):
            return jsonify({'message': '发送成功'}), 200
        else:
            raise Exception('错误2:发送失败')
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400
 

 # 验证验证码
@stu_bp.route('/verify_code', methods=['POST'])
@jwt_required()
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