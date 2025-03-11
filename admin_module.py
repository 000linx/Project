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
dormitorynotice_collection = db['dormitorynotice']
notice_collection = db['notifications']
visitor_collection = db['visitor']
excluded_fields = ['password','_id']
stu_collection = db['student']

# 创建管理员蓝图
admin_bp = Blueprint('admin', __name__)

'''
管理端接口统计
'''

# 管理员登录
@admin_bp.route('/adminLogin', methods=['POST'])
def login():
    try:
        data = request.get_json()
        account = data['account']
        password = data['password']
        if account is None or password is None:
            raise Exception("错误0:账户或密码为空")
        admin = admin_collection.find_one({'Account':account})
        if admin is None:
            raise Exception("错误1:用户不存在")
        if not check_password_hash(admin['Password'],password):
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
    
# 管理员信息
@admin_bp.route('/adminInfo', methods=['POST'])
@jwt_required()
def adminInfo():
    try:
        current_user = get_jwt_identity()
        account = request.get_json()['account']
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        admin = admin_collection.find_one({'Account':account},{'_id':0})
        return jsonify(admin),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400

# 申请处理
@admin_bp.route('/dormApply', methods=['POST'])
@jwt_required()
def apply():
    try:
        current_user = get_jwt_identity()
        account = request.get_json()['account']
        OnlyID = request.get_json()['OnlyID']
        State = request.get_json()['State']
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        if OnlyID is None:
            raise Exception("参数缺少")
        dormitory_collection.update_one({"OnlyID":OnlyID},{"$set":{"State":State}})
        return jsonify("处理成功"),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400

# 管理员访客处理
@admin_bp.route('/adminAgreeVisitor', methods=['POST'])
@jwt_required()
def adminAgreeVisitor():
    try:
        data = request.get_json()
        current_user = get_jwt_identity()
        account = data['account']
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        StudentID = data['StudentID']
        VisitorID = data['VisitorID']
        adminState =  data['adminState']
        if VisitorID is None or StudentID is None:
            raise Exception ("参数缺少")
        visitor_collection.update_one({"VisitorID":VisitorID},{"$set":{"adminState":adminState}})
        return jsonify({"message":"处理成功"}),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400
    
# 单个宿舍申请通知
@admin_bp.route('/dormNotice', methods=['POST'])
@jwt_required()
def dormNotice():
    try:
        data = request.get_json()
        current_user = get_jwt_identity()
        account = data['account']
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        OnlyID = data['OnlyID']
        dorm = dormitorynotice_collection.find_one({"OnlyID":OnlyID},{'_id':0})
        return jsonify(dorm),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400
    
# 全部宿舍申请通知
@admin_bp.route('/allDormNotice', methods=['POST'])
@jwt_required()
def allDormNotice():
    try:
        current_user = get_jwt_identity()
        account = request.get_json()['account']
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        dorms = dormitorynotice_collection.find({},{'_id':0})
        dorms_list = list(dorms)
        return jsonify(dorms_list),200        
    except Exception as e:
        return jsonify("发生异常",str(e)),400
    

# 发布宿舍通知
@admin_bp.route('/publishNotice', methods=['POST'])
@jwt_required()
def publishNotice():
    try:
        current_user = get_jwt_identity()
        account = request.get_json()['account']
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        data = request.get_json()
        Publisher = data['Publisher']
        Title = data['Title']
        Content = data['Content']
        Time = data['Time']
        if Publisher is None or Title is None or Content is None or Time is None:
            raise Exception("参数缺少")
        Noticeid = notice_collection.count_documents({})+1
        notice_collection.insert_one({"noticeid":Noticeid,"Publisher":Publisher,"Title":Title,"Content":Content,"Time":Time})
        return jsonify("发布成功"),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400

# 删除宿舍通知
@admin_bp.route('/deleteNotice', methods=['POST'])
@jwt_required()
def delete():
    try:
        current_user = get_jwt_identity()
        account = request.get_json()['account']
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        data = request.get_json()
        noticeid = data['noticeid']
        if noticeid is None:
            raise Exception("参数缺少")
        notice_collection.delete_one({"noticeid":noticeid})
        return jsonify("删除成功"),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400
    
# 添加学生
@admin_bp.route('/addStudent', methods=['POST'])
@jwt_required()
def addStudent():
    try:
        current_user = get_jwt_identity()
        account = request.get_json()['account']
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        data = request.get_json()
        GraduationStatus = data['GraduationStatus']
        Faculty = data['Faculty']
        Professional = data['Professional']
        Grade = data['Grade']
        Class = data['Class']
        Duration = data['Duration']
        EnrollmentDate = data['EnrollmentDate']
        GraduationDate = data['GraduationDate']
        StudentID = data['StudentID']
        Counselor = data['Counselor']
        CounselorPhoneNumber = data['CounselorPhoneNumber']
        password = data['password']
        password = generate_password_hash(password)
        Building = data['Building']
        DormitoryID = data['DormitoryID']
        BedNumber = data['BedNumber']
        account = data['Newaccount']
        Name = data['Name']
        if GraduationStatus is None or Faculty is None or Professional is None or Grade is None or Class is None or Duration is None or EnrollmentDate is None or StudentID is None or Counselor is None or CounselorPhoneNumber is None or password is None or Building is None or DormitoryID is None or BedNumber is None or account is None:
            raise Exception("参数缺少")
        BaseInfo = {
            "Name":Name,
            "StudentID":StudentID,
            "Counselor":Counselor,
            "CounselorPhoneNumber":CounselorPhoneNumber,
        }
        EducationInfo = {
            "GraduationStatus":GraduationStatus,
            "Faculty":Faculty,
            "Professional":Professional,
            "Grade":Grade,
            "Class":Class,
            "Duration":Duration,
            "EnrollmentDate":EnrollmentDate, 
            "GraduationDate":GraduationDate
        }
        stu_collection.insert_one({"account":account,"password":password,"Role":"user","DormitoryBuilding":Building,"DormitoryID":DormitoryID,"BedNumber":BedNumber,"BaseInfo":BaseInfo,"EducationInfo":EducationInfo,})
        return jsonify({"message":"添加成功"}),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400
# 删除学生
@admin_bp.route('/deleteStudent', methods=['POST'])
@jwt_required()
def deleteStudent():
    try:
        data = request.get_json()
        account = data['account']
        if account is None:
            raise Exception("错误0:账户为空")
        DormitoryID = data['DormitoryID']
        BedNumber = data['BedNumber']
        if DormitoryID is None or BedNumber is None:
            raise Exception("参数缺少")
        stu_collection.delete_one({"account":account})
        return jsonify({"message":"删除成功"}),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400

# 添加管理员
@admin_bp.route('/addAdmin', methods=['POST'])
@jwt_required()
def addAdmin():
    try:
        current_user = get_jwt_identity()
        account = request.get_json()['account']
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        data = request.get_json()
        Name = data['Name']
        Position = data['Position']
        TeacherID = data['TeacherID']
        PhoneNumber = data['PhoneNumber']
        account = data['Newaccount']
        password = data['password']
        Email = data['Email']
        password = generate_password_hash(password)
        if account is None or password is None:
            raise Exception("参数缺少")
        admin_collection.insert_one({"Name":Name,'Role':'admin',"Position":Position,"TeacherID":TeacherID,"PhoneNumber":PhoneNumber,"Email":Email,"account":account,"password":password})
        return jsonify({"message":"添加成功"}),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400

# 修改管理员信息
@admin_bp.route('/updateAdmin', methods=['POST'])
@jwt_required()
def updateAdmin():
    try:
        data = request.get_json()
        current_user = get_jwt_identity()
        account = data['account']
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        Name = data['Name']
        Position = data['Position']
        TeacherID = data['TeacherID']
        PhoneNumber = data['PhoneNumber']
        Email = data['Email']
        if Name is None or Position is None or TeacherID is None or PhoneNumber is None or Email is None:
            raise Exception("参数缺少")
        admin_collection.update_one({"account":account},{"$set":{"Name":Name,"Position":Position,"TeacherID":TeacherID,"PhoneNumber":PhoneNumber,"Email":Email}})
        return jsonify({"message":"修改成功"}),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400

# 删除管理员
@admin_bp.route('/deleteAdmin', methods=['POST'])
@jwt_required()
def deleteAdmin():
    try:
        data = request.get_json()
        account = data['account']
        TeacherID = data['TeacherID']
        if account is None or TeacherID is None:
            raise Exception("参数缺少")
        if account is None:
            raise Exception("错误0:账户为空")
        admin_collection.delete_one({"account":account})
        return jsonify({"message":"删除成功"}),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400
    
# 管理忘记密码
@admin_bp.route('/adminForgetPwd', methods=['POST'])
def adminforgetPassword():
    try:
        data = request.get_json()
        account = data['account']
        password = data['password']
        if account is None or password is None:
            raise Exception("参数缺少")
        admin_collection.update_one({"account":account},{"$set":{"password":generate_password_hash(password)}})
        return jsonify({"message":"修改成功"}),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400