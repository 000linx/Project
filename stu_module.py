from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity,get_jwt
from flask import Blueprint, request, jsonify,session
from werkzeug.security import check_password_hash, generate_password_hash
from pymongo import MongoClient
from datetime import timedelta
from utils import *

'''
学生模块接口统计
1. 学生登录
2. 退出登录
3. 获取个人信息
4. 修改个人信息
5. 获取单个通知
6. 获取全部通知
7. 获取单个报修记录
8. 获取全部报修记录
9. 获取宿舍信息
10. 学生更换宿舍
11. 学生申请退宿
12. 学生假期退宿
13. 单个访客信息
14. 全部访客信息
15. 学生访客申请
16. 取消访问申请
17. 修改密码
'''


# 数据库配置以及连接
client = MongoClient('mongodb://localhost:27017/')
db = client['Student_Dormitory']
stu_collection = db['student']
notice_collection = db['notifications']
repair_collection = db['repaires']
mydormitory_collection = db['mydormitory']
visitor_collection = db['visitor']
dormitory_collection = db['dormitorynotice']
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
        StudentID = data['StudentID']
        phone = data['Phone']
        email = data['Email']
        QQNumber = data['QQNumber']
        Address = data['Address']
        verification_code = data['verification_code']
        if StudentID is None or phone is None or email is None or QQNumber is None or Address is None:
            raise Exception('错误0:请求参数为空')
        if verification_code is None:
            raise Exception('错误1:验证码为空')
        stored_code = session.get('verification_code')
        if stored_code is None:
            raise Exception('错误2:验证码已过期或不存在')
        if verification_code != stored_code:
            raise Exception('错误3:验证码错误')
        current_user = get_jwt_identity()
        if check_identity(current_user, StudentID) == False:
            raise Exception('错误4:当前用户错误')
        stu = stu_collection.find_one({'StudentID': StudentID})
        if stu is None:
            raise Exception('错误5:当前用户不存在')
        stu_collection.update_one({'$set': {'Phone': phone, 'Email': email, 'QQNumber': QQNumber, 'Address': Address}})

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
        NoticeID = data['NoticeID']
        if StudentID is None or NoticeID is None:
            raise Exception('错误0:学号或通知id为空')
        current_user = get_jwt_identity()
        if check_identity(current_user, StudentID) == False:
            raise Exception('错误1:当前用户错误')
        notice = notice_collection.find_one({'NoticeID': NoticeID,'StudentID':StudentID},{'_id':0})
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
        notices = notice_collection.find({'StudentID' : StudentID},{'_id':0})
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
        StudentID = data['StudentID']
        RepairID = data['RepairID']
        if StudentID is None or RepairID is None:
            raise Exception('学号或报修id为空')
        current_user = get_jwt_identity()
        if check_identity(current_user, StudentID) == False:
            raise Exception('当前用户错误')
        repair = repair_collection.find_one({'RepairID': RepairID, "StudentID": StudentID},{'_id':0})
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
        StudentID = data['StudentID']
        current_user = get_jwt_identity()
        if check_identity(current_user, StudentID) == False:
            raise Exception('当前用户错误')
        repairs = repair_collection.find({'StudentID': StudentID},{'_id':0})
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
        stuid = data['StudentID']
        dormitoryid = data['DormitoryID']
        if stuid is None or dormitoryid is None:
            raise Exception('学号或宿舍id为空')
        current_user = get_jwt_identity()
        if check_identity(current_user, stuid) == False:
            return jsonify({'message': '用户错误'}), 400
        dormitory = mydormitory_collection.find_one({'DormitoryID':dormitoryid},{'_id':0})
        if dormitory is None:
            raise Exception('当前宿舍不存在')
        return jsonify({'message': '获取成功','DormitoryID':dormitory}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400

# 学生更换宿舍申请
@stu_bp.route('/StuExchangeDormitory', methods=['POST'])
@jwt_required()
def exchange_dormitory():
    try:
        data = request.get_json()
        StudentName = data['StudentName']
        StudentID = data['StudentID']
        Building = data['Building']
        DormitoryID = data['DormitoryID']
        BedNumber = data['BedNumber']
        NewStudentName = data['NewStudentName']
        NewStudentID = data['NewStudentID']
        NewBuilding = data['NewBuilding']
        NewDormitoryID = data['NewDormitoryID']
        NewBedNumber = data['NewBedNumber']
        Reason = data['Reason']
        OnlyID = generate_OnlyID()
        current_user = get_jwt_identity()
        if check_identity(current_user, StudentID) == False:
            raise Exception('当前用户错误')
        if StudentName is None or StudentID is None or Building is None or DormitoryID is None or BedNumber is None or NewStudentName is None or NewStudentID is None or NewBuilding is None or NewDormitoryID is None or NewBedNumber is None or Reason is None:
            raise Exception('请求参数包含空值')
        dormitory_collection.insert_one({'Title':'换宿申请','StudentName':StudentName,'StudentID':StudentID,'Building':Building,'DormitoryID':DormitoryID,'BedNumber':BedNumber,'NewStudentName':NewStudentName,'NewStudentID':NewStudentID,'NewBuilding':NewBuilding,'NewDormitoryID':NewDormitoryID,'NewBedNumber':NewBedNumber,'Reason':Reason,'state':'待审核','OnlyID':OnlyID}) 
        return jsonify({'message':'申请成功'}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400

# 学生申请退宿
@stu_bp.route('/StuQuitDormitory', methods=['POST'])
@jwt_required()
def quit_dormitory():
    try:
        data = request.get_json()
        StudentName = data['StudentName']
        StudentID = data['StudentID']
        DormitoryID = data['DormitoryID']
        Reason = data['Reason']
        OnlyID = generate_OnlyID()
        current_user = get_jwt_identity()
        if check_identity(current_user, StudentID) == False:
            raise Exception('当前用户错误')
        dormitory = mydormitory_collection.find_one({'DormitoryID':DormitoryID})
        if dormitory is None:
            raise Exception('当前宿舍不存在')
        dormitory_collection.insert_one({'Title':'退宿申请','StudentName':StudentName,'StudentID':StudentID,'DormitoryID':DormitoryID,'Reason':Reason,'state':'待审核','OnlyID':OnlyID})
        return jsonify({'message':'申请成功'}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400
# 学生假期留宿
@stu_bp.route('/StuStayDormitory', methods=['POST'])
@jwt_required()
def stay_dormitory():
    try:
        data = request.get_json()
        StudentName = data['StudentName']
        StudentID = data['StudentID']
        DormitoryID = data['DormitoryID']
        Reason = data['Reason']
        StartTime = data['StartTime']
        EndTime = data['EndTime']
        OnlyID = generate_OnlyID()
        current_user = get_jwt_identity()
        if check_identity(current_user, StudentID) == False:
            return jsonify({'message':'当前用户错误'}), 400
        if StartTime is None or EndTime is None or Reason is None or DormitoryID is None or StudentID is None or StudentName is None:
            return jsonify({'message':'参数缺少'}), 400
        dormitory_collection.insert_one({'Title':'留宿申请','StudentName':StudentName,'StudentID':StudentID,'DormitoryID':DormitoryID,'Reason':Reason,'state':'待审核','StartTime':StartTime,'EndTime':EndTime,'OnlyID':OnlyID})
        return jsonify({'message':'申请成功'}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400
    

#####################################################################################################
# 学生访客
# 单个访客信息
@stu_bp.route('/StuVisitor', methods=['POST'])
@jwt_required()
def get_visitor():
    try:
        data = request.get_json()
        StudentID = data['StudentID']
        VisitorID = data['VisitorID']
        current_user = get_jwt_identity()
        if check_identity(current_user, StudentID) == False:
            raise Exception('当前用户错误')
        visitor = visitor_collection.find_one({'StudentID':StudentID,'VisitorID':VisitorID},{'_id':0})
        if visitor is not None:
            return jsonify({'message':'获取成功','visitor':visitor}), 200
        else:
            raise Exception('当前访客不存在')
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400
# 全部访客信息
@stu_bp.route('/StuVisitors', methods=['POST'])
@jwt_required()
def get_visitors():
    try:
        data = request.get_json()
        StudentID = data['StudentID']
        current_user = get_jwt_identity()
        if check_identity(current_user, StudentID) == False:
            raise Exception('当前用户错误')
        visitors = visitor_collection.find({'StudentID':StudentID},{'_id':0})
        if visitors is not None:
            visitors_list = []
            for visitor in visitors:
                visitors_list.append(visitor)
            return jsonify({'message':'获取成功','visitors':visitors_list}), 200
        else:
            raise Exception('当前访客为空')
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400

# 学生访客申请
@stu_bp.route('/StuApplyVisitor', methods=['POST'])
@jwt_required()
def apply_visitor():
    try:
        data = request.get_json()
        StudentName = data['StudentName']
        StudentID = data['StudentID']
        VisitorID = data['VisitorID']
        VisitorName = data['VisitorName']
        VisitorPhone = data['VisitorPhone']
        Relationship = data['Relationship']
        Reason = data['Reason']
        StartTime = data['StartTime']
        Duration = data['Duration']
        current_user = get_jwt_identity()
        if check_identity(current_user, StudentID) == False:
            raise Exception('当前用户错误')
        Visitorinfo = {
            'VisitorName':VisitorName,
            'VisitorPhone':VisitorPhone,
            'Relationship':Relationship,
            'Reason':Reason,
            'StartTime':StartTime,
            'Duration':Duration
        }
        state = '待审核'
        visitor_collection.insert_one({'StudentName':StudentName,'StudentID':StudentID,'VisitorID':VisitorID,'State':state,'Visitorinfo':Visitorinfo})
        return jsonify({'message':'申请成功'}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400

# 取消访问申请
@stu_bp.route('/StuCancelVisitor', methods=['POST'])
@jwt_required()
def cancel_visitor():
    try:
        data = request.get_json()
        StudentID = data['StudentID']
        VisitorID = data['VisitorID']
        current_user = get_jwt_identity()
        if check_identity(current_user, StudentID) == False:
            raise Exception('当前用户错误')
        visitor = visitor_collection.find_one({'StudentID':StudentID,'VisitorID':VisitorID})
        if visitor is not None:
            visitor_collection.delete_one({'StudentID':StudentID,'VisitorID':VisitorID})
            return jsonify({'message':'取消成功'}), 200
        else:
            raise Exception('当前访客不存在')
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400

#####################################################################################################
# 修改密码
@stu_bp.route('/StuChangePwd', methods=['POST'])
@jwt_required()
def change_pwd():
    try:
        data = request.get_json()
        StudentID = data['StudentID']
        OldPwd = data['OldPwd']
        NewPwd = data['NewPwd']
        if StudentID is None or OldPwd is None or NewPwd is None:
            raise Exception('请求参数包含空值')
        current_user = get_jwt_identity()
        if check_identity(current_user, StudentID) == False:
            raise Exception('当前用户错误')
        student = stu_collection.find_one({'StudentID':StudentID})
        if student is None:
            raise Exception('当前用户不存在')
        if check_password_hash(student['password'], OldPwd):
            stu_collection.update_one({'StudentID':StudentID},{'$set':{'password':generate_password_hash(NewPwd)}})
            return jsonify({'message':'修改成功'}), 200
        else:
            raise Exception('旧密码错误')
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400
