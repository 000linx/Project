from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity,get_jwt
from flask import Blueprint, request, jsonify,session
from werkzeug.security import check_password_hash, generate_password_hash
from pymongo import MongoClient
from datetime import datetime
from utils import *

'''
学生模块接口统计
1. 学生登录
2. 退出登录
3. 获取个人信息
4. 修改个人信息
5. 获取单个通知
6. 获取全部通知
7. 报修申请
8. 获取单个报修记录
9. 获取全部报修记录
10. 获取宿舍信息
11. 更换宿舍申请
12. 申请退宿
13. 假期留宿
14. 获取单个访客信息
15. 获取全部访客信息
16. 访客申请
17. 取消访客申请
18. 修改密码

'''

# 数据库配置以及连接
client = MongoClient('mongodb://localhost:27017/')
db = client['Student_Dormitory']
stu_collection = db['student']
notice_collection = db['notifications'] #其他通知
mydormitory_collection = db['mydormitory']
visitor_collection = db['visitor']
dormitorynotice_collection = db['dormitorynotice'] #宿舍通知
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
        account = data['StudentID']
        password = data['password']
        if account is None or password is None:
            raise Exception('错误1:账号或密码为空')
        student = stu_collection.find_one({ "account": account })
        if student is not None:
            if check_password_hash(student['password'], password):
                access_token = create_access_token(identity=generate_identity(account))
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
    
    # 忘记密码
@stu_bp.route('/StuForgetPwd', methods=['POST'])
def forget_pwd():
    try:
        data = request.get_json()
        account = data['account']
        password = data['password']
        if account is None or password is None:
            raise Exception('错误0:账号或密码为空')
        stu = stu_collection.find_one({'account': account})
        if stu is None:
            raise Exception('错误1:用户不存在')
        stu_collection.update_one({'account': account}, {'$set': {'password': generate_password_hash(password)}})
        return jsonify({'message': '修改成功'}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400

# 修改密码
@stu_bp.route('/StuChangePwd', methods=['POST'])
@jwt_required()
def change_pwd():
    try:
        data = request.get_json()
        account = data['account']
        OldPwd = data['OldPwd']
        NewPwd = data['NewPwd']
        if account is None or OldPwd is None or NewPwd is None:
            raise Exception('请求参数包含空值')
        current_user = get_jwt_identity()
        if check_identity(current_user, account) == False:
            raise Exception('当前用户错误')
        student = stu_collection.find_one({'account':account})
        if student is None:
            raise Exception('当前用户不存在')
        if check_password_hash(student['password'], OldPwd):
            stu_collection.update_one({'account':account},{'$set':{'password':generate_password_hash(NewPwd)}})
            return jsonify({'message':'修改成功'}), 200
        else:
            raise Exception('旧密码错误')
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
        account = data['StudentID']
        if account is None:
            raise Exception('错误0:学号为空')
        if check_identity(current_user, account) == False:
           raise Exception('错误1:用户错误') 
        stu = stu_collection.find_one({'account': account},{filed: 0 for filed in excluded_fields})
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
       info = request.get_json()['info']
       current_user = get_jwt_identity()
       account = info['account']
       if check_identity(current_user, account) == False:
           raise Exception('错误0:用户错误')
       Role = info['Role']
       DormitoryBuilding = info['DormitoryBuilding']
       DormitoryID = info['DormitoryID']
       BedNumber = info['BedNumber']
       Base_info = info.get('BaseInfo')
       ContactInfo = info.get('ContactInfo')
       EducationInfo = info.get('EducationInfo')
       FamilyInfo = info.get('FamilyInfo')
       stu_collection.update_one({"account":account},{"$set":{"Role":Role,"DormitoryBuilding":DormitoryBuilding,"DormitoryID":DormitoryID,"BedNumber":BedNumber,"BaseInfo":Base_info,"ContactInfo":ContactInfo,"EducationInfo":EducationInfo,"FamilyInfo":FamilyInfo}})
       return jsonify({'message': '修改成功'}), 200
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
        notice = notice_collection.find_one({'Noticeid': NoticeID},{'_id':0})
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
# 报修申请
@stu_bp.route('/StuRepairApply', methods=['POST'])
@jwt_required()
def repair_apply():
    try:
        data = request.get_json()
        StudentID = data['StudentID']
        StudentName = data['StudentName']
        PhoneNumber = data['PhoneNumber']
        DormitoryID = data['DormitoryID']
        Equipment = data['Equipment']
        Applytime = datetime.now().strftime("%Y-%m-%d %H:%M")
        Dealtime = datetime.now().strftime("%Y-%m-%d %H:%M")
        Reason = data['Reason']
        OnlyID = generate_OnlyID()
        current_user = get_jwt_identity()
        if check_identity(current_user, StudentID) == False:
            raise Exception('当前用户错误')
        if StudentID is None or StudentName is None or DormitoryID is None or Equipment is None or Reason is None or PhoneNumber is None:
            raise Exception('请求参数包含空值')
        equipments = mydormitory_collection.find_one({'DormitoryID':DormitoryID},{'_id':0,'equipments':1})
        if equipments is None:
            raise Exception('当前宿舍不存在')
        equipments_list = equipments['equipments']
        for item in equipments_list:
            if item['name'] == Equipment:
                mydormitory_collection.update_one(
                {'DormitoryID':DormitoryID,'equipments.name':Equipment},
                {'$set':{'equipments.$.state':'损坏'}}
                )
        dormitorynotice_collection.insert_one(
            {
            'Title':'报修申请',
            'StudentID':StudentID,'StudentName':StudentName,'PhoneNumber':PhoneNumber,'DormitoryID':DormitoryID,'Equipment':Equipment,'Reason':Reason,'State':'待处理','stuState':'未完成',
            'Applytime':Applytime,'Dealtime':Dealtime,'OnlyID':OnlyID
            }
            )
        return jsonify({'message':'申请成功'}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400
    
# 获取单个申请记录
@stu_bp.route('/Stuapply', methods=['POST'])
@jwt_required()
def get_repaire():
    try:
        data = request.get_json()
        StudentID = data['StudentID']
        OnlyID = data['OnlyID']
        if StudentID is None or OnlyID is None:
            raise Exception('学号或id为空')
        current_user = get_jwt_identity()
        if check_identity(current_user, StudentID) == False:
            raise Exception('当前用户错误')
        apply = dormitorynotice_collection.find_one({'OnlyID':OnlyID},{'_id':0})
        if apply is None:
            raise Exception('当前申请记录不存在')
        else :
            return jsonify({'message': '获取成功','apply': apply}),200
            
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400

# 获取全部申请记录
@stu_bp.route('/StuallDormApply', methods=['POST'])
@jwt_required()
def get_repairs():
    try:
        data = request.get_json()
        StudentID = data['StudentID']
        Title = data['Title']

        current_user = get_jwt_identity()
        if check_identity(current_user, StudentID) == False:
            raise Exception('当前用户错误')
        apply_a = dormitorynotice_collection.find({'StudentID': StudentID,'Title':Title},{'_id':0})
        apply_b = dormitorynotice_collection.find({'NewStudentID': StudentID,'Title':Title},{'_id':0})
        if apply_a is None and apply_b is None:
            return jsonify({'message': '当前无申请记录'}), 200
        apply_a = list(apply_a)
        apply_b = list(apply_b)
        return jsonify({'message': '获取成功','applys':apply_a or apply_b}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400
    
# 报修完成确认
@stu_bp.route('/StuRepairConfirm', methods=['POST'])
@jwt_required()
def repair_confirm():
    try:
        data = request.get_json()
        StudentID = data['StudentID']
        OnlyID = data['OnlyID']
        stuState = data['stuState']
        current_user = get_jwt_identity()
        if check_identity(current_user, StudentID) == False:
            raise Exception('当前用户错误')
        if StudentID is None or OnlyID is None:
            raise Exception('学号或报修id为空')
        if stuState == '已完成':
            dormitorynotice_collection.update_one(
                {'OnlyID':OnlyID,'StudentID':StudentID},
                {'$set':{'stuState':stuState}} 
            )
            Equipment = dormitorynotice_collection.find_one({'OnlyID':OnlyID,'StudentID':StudentID},{'_id':0,'Equipment':1})['Equipment']
            DormitoryID = dormitorynotice_collection.find_one({'OnlyID':OnlyID,'StudentID':StudentID},{'_id':0,'DormitoryID':1})['DormitoryID']
            Equipments = mydormitory_collection.find_one({'DormitoryID':DormitoryID},{'_id':0,'equipments':1})['equipments']
            for item in Equipments:
                if item['name'] == Equipment:
                    mydormitory_collection.update_one(
                        {'DormitoryID':DormitoryID,'equipments.name':Equipment},
                        {'$set':{'equipments.$.state':'正常'}}
                    )
        return jsonify({'message': '确认成功'}), 200
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
            raise Exception('当前用户错误')
        dormitory = mydormitory_collection.find_one(
            {'DormitoryID':dormitoryid},
            {'_id':0,'roommatesinfo':1,'location':1,'equipments':1}
        )
        if not dormitory:
            raise Exception('当前宿舍不存在')
        location = dormitory['location']
        roommate_info = dormitory.get('roommatesinfo',[])
        equipments = dormitory.get('equipments',[])
        target_student = None
        filtered_roommates = []
        for student in roommate_info:
            if student.get('StudentID') == stuid:
                target_student = student
            else:
                filtered_roommates.append(student)
        if not target_student:
            raise Exception('该学生不在这个宿舍中')        
        response_data = {
            "location":location,
            "DormitoryID": dormitoryid,
            "BedNumber": target_student.get('BedNumber'),
            "roommates": filtered_roommates,
            "equipments": equipments 
        }
        return jsonify(response_data)

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
        stuAstate = "同意"
        stuBstate = "待处理"
        Applytime = datetime.now().strftime("%Y-%m-%d %H:%M")
        Dealtime = datetime.now().strftime("%Y-%m-%d %H:%M")
        OnlyID = generate_OnlyID()
        current_user = get_jwt_identity()
        if check_identity(current_user, StudentID) == False:
            raise Exception('当前用户错误')
        if StudentName is None or StudentID is None or Building is None or DormitoryID is None or BedNumber is None or NewStudentName is None or NewStudentID is None or NewBuilding is None or NewDormitoryID is None or NewBedNumber is None or Reason is None:
            raise Exception('请求参数包含空值')
        dormitorynotice_collection.insert_one({
            'Title':'换宿申请',
            'StudentName':StudentName,'StudentID':StudentID,'StuAstate':stuAstate,'Building':Building,'DormitoryID':DormitoryID,'BedNumber':BedNumber,
            'NewStudentName':NewStudentName,'NewStudentID':NewStudentID,'StuBstate':stuBstate,'NewBuilding':NewBuilding,'NewDormitoryID':NewDormitoryID,'NewBedNumber':NewBedNumber,
            'Applytime':Applytime,'Dealtime':Dealtime,
            'Reason':Reason,'State':'待审核','OnlyID':OnlyID,
            }) 
        return jsonify({'message':'申请成功'}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400

# 学生同意换宿申请
@stu_bp.route('/StuAgreeExchange', methods=['POST'])
@jwt_required()
def agree_exchange():
    try:
        data = request.get_json()
        StudentID = data['StudentID']
        Dealtime = datetime.now().strftime("%Y-%m-%d %H:%M")
        OnlyID = data['OnlyID']
        stuBstate = data['stuState']
        current_user = get_jwt_identity()
        if check_identity(current_user, StudentID) == False:
            raise Exception('当前用户错误')
        notice = dormitorynotice_collection.find_one({'OnlyID':OnlyID})
        if notice is None:
            raise Exception('当前通知不存在')
        if notice['StuBstate'] == '待处理':
            dormitorynotice_collection.update_one({'OnlyID':OnlyID},{'$set':{'StuBstate':stuBstate,'Dealtime':Dealtime}})
        else:
            raise Exception('当前通知已处理')
        return jsonify({'message':'同意成功'})
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400

# 学生撤销申请
@stu_bp.route('/StuCancelApple', methods=['POST'])
@jwt_required()
def cancel():
    try:
        data = request.get_json()
        StudentID = data['StudentID']
        Dealtime = datetime.now().strftime("%Y-%m-%d %H:%M")
        OnlyID = data['OnlyID']
        current_user = get_jwt_identity()
        if check_identity(current_user, StudentID) == False:
            raise Exception('当前用户错误')
        notice = dormitorynotice_collection.find_one({'OnlyID':OnlyID})
        if notice is None:
            raise Exception('当前通知不存在')
        if notice['State'] == '待审核':
            dormitorynotice_collection.update_one({'OnlyID':OnlyID},{'$set':{'State':'已撤销','Dealtime':Dealtime}})
            return jsonify({'message':'撤销成功'}), 200
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
        Applytime = datetime.now().strftime("%Y-%m-%d %H:%M")
        Dealtime = datetime.now().strftime("%Y-%m-%d %H:%M")
        OnlyID = generate_OnlyID()
        current_user = get_jwt_identity()
        if check_identity(current_user, StudentID) == False:
            raise Exception('当前用户错误')
        dormitory = mydormitory_collection.find_one({'DormitoryID':DormitoryID})
        if dormitory is None:
            raise Exception('当前宿舍不存在')
        dormitorynotice_collection.insert_one({
            'Title':'退宿申请',
            'StudentName':StudentName,'StudentID':StudentID,'DormitoryID':DormitoryID,'Reason':Reason,
            'Applytime':Applytime,'Dealtime':Dealtime,
            'State':'待审核','OnlyID':OnlyID
            })
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
        Applytime = datetime.now().strftime("%Y-%m-%d %H:%M")
        Dealtime = datetime.now().strftime("%Y-%m-%d %H:%M")
        OnlyID = generate_OnlyID()
        current_user = get_jwt_identity()
        if check_identity(current_user, StudentID) == False:
            return jsonify({'message':'当前用户错误'}), 400
        if StartTime is None or EndTime is None or Reason is None or DormitoryID is None or StudentID is None or StudentName is None:
            return jsonify({'message':'参数缺少'}), 400
        dormitorynotice_collection.insert_one({
            'Title':'留宿申请',
            'StudentName':StudentName,'StudentID':StudentID,'DormitoryID':DormitoryID,'Reason':Reason,
            'StartTime':StartTime,'EndTime':EndTime,'Applytime':Applytime,'Dealtime':Dealtime,
            'State':'待审核','OnlyID':OnlyID
            })
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
def apply_visitor():
    try:
        
        data = request.get_json()
        StudentName = data['StudentName']
        StudentID = data['StudentID']
        DormitoryID = data['DormitoryID']
        VisitorName = data['VisitorName']
        VisitorPhone = data['VisitorPhone']
        Relationship = data['Relationship']
        Reason = data['Reason']
        StartTime = data['StartTime']
        Duration = data['Duration']
        if StudentName is None or StudentID is None or DormitoryID is None or VisitorName is None or VisitorPhone is None or Relationship is None or Reason is None or StartTime is None or Duration is None:
            raise Exception('请求参数包含空值')
        Applytime = datetime.now().strftime("%Y-%m-%d %H:%M")
        Dealtime = datetime.now().strftime("%Y-%m-%d %H:%M")
        Visitorinfo = {
            'VisitorName':VisitorName,
            'VisitorPhone':VisitorPhone,
            'Relationship':Relationship,
            'Reason':Reason,
            'StartTime':StartTime,
            'Duration':Duration,
            'Applytime':Applytime,
            'Dealtime':Dealtime
        }
        student = stu_collection.find_one({'account':StudentID},{'_id':0})
        if student is None:
            raise Exception('当前学生不存在')
        VisitorID = visitor_collection.count_documents({}) + 1
        visitor_collection.insert_one({
            'StudentName':StudentName,'StudentID':StudentID,'DormitoryID':DormitoryID,'VisitorID':str(VisitorID),
            'stuState':'待同意','adminState':'待审核',
            'Visitorinfo':Visitorinfo
            })
        return jsonify({'message':'申请成功'}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400

# 同意访问申请
@stu_bp.route('/StuAgreeVisitor', methods=['POST'])
@jwt_required()
def agree_visitor():
    try:
        data = request.get_json()
        StudentID = data['StudentID']
        VisitorID = data['VisitorID']
        stuState = data['stuState']
        Applytime = datetime.now().strftime("%Y-%m-%d %H:%M")
        current_user = get_jwt_identity()
        if check_identity(current_user, StudentID) == False:
            raise Exception('当前用户错误')
        visitor = visitor_collection.find_one({'StudentID':StudentID,'VisitorID':VisitorID})
        if visitor is None:
            raise Exception('当前访客不存在')
        visitor_collection.update_one({'StudentID':StudentID,'VisitorID':VisitorID},{'$set':{'stuState':stuState,'Applytime':Applytime}})
        return jsonify({'message':'同意成功'}), 200
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400


# # 取消访问申请
# @stu_bp.route('/StuCancelVisitor', methods=['POST'])
# @jwt_required()
# def cancel_visitor():
#     try:
#         data = request.get_json()
#         StudentID = data['StudentID']
#         VisitorID = data['VisitorID']
#         current_user = get_jwt_identity()
#         if check_identity(current_user, StudentID) == False:
#             raise Exception('当前用户错误')
#         visitor = visitor_collection.find_one({'StudentID':StudentID,'VisitorID':VisitorID})
#         if visitor is not None:
#             visitor_collection.delete_one({'StudentID':StudentID,'VisitorID':VisitorID})
#             return jsonify({'message':'取消成功'}), 200
#         else:
#             raise Exception('当前访客不存在')
#     except Exception as e:
#         return jsonify({"发生异常":str(e)}), 400

#####################################################################################################
