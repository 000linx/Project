from datetime import datetime
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
mydormitory_collection = db['mydormitory']
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
    
# 管理员信息
@admin_bp.route('/adminInfo', methods=['POST'])
@jwt_required()
def adminInfo():
    try:
        current_user = get_jwt_identity()
        account = request.get_json()['account']
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        admin = admin_collection.find_one({'account':account},{'_id':0,'password':0})
        return jsonify(admin),200
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

# 删除管理员
@admin_bp.route('/deleteAdmin', methods=['POST'])
@jwt_required()
def deleteAdmin():
    try:
        data = request.get_json()
        account = data['account']
        current_user = get_jwt_identity()
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
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
    
# 修改密码
@admin_bp.route('/adminChangePwd', methods=['POST'])
@jwt_required()
def changepwd():
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
        admin = admin_collection.find_one({'account':account})
        if admin is None:
            
            raise Exception('当前用户不存在')
        if check_password_hash(admin['password'], OldPwd):
            admin_collection.update_one({'account':account},{'$set':{'password':generate_password_hash(NewPwd)}})
            return jsonify({'message':'修改成功'}), 200
        else:
            raise Exception('旧密码错误')
    except Exception as e:
        return jsonify({"发生异常":str(e)}), 400

# 申请处理
@admin_bp.route('/dormApply', methods=['POST'])
@jwt_required()
def apply():
    try:
        current_user = get_jwt_identity()
        account = request.get_json()['account']
        OnlyID = request.get_json()['OnlyID']
        Title = request.get_json()['Title']
        State = request.get_json()['State']
        Dealtime = datetime.now().strftime("%Y-%m-%d %H:%M")
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        if OnlyID is None:
            raise Exception("参数缺少")
        if Title == '报修申请':
            DormitoryID = dormitorynotice_collection.find_one({"OnlyID":OnlyID})['DormitoryID']
            Equipment = dormitorynotice_collection.find_one({"OnlyID":OnlyID})['Equipment']
            equipments = mydormitory_collection.find_one({'DormitoryID':DormitoryID},{'_id':0,'equipments':1})
            equipments_list = equipments['equipments']
            for item in equipments_list:
                if item['name'] == Equipment and State == '已处理':
                    mydormitory_collection.update_one(
                    {'DormitoryID':DormitoryID,'equipments.name':Equipment},
                    {'$set':{'equipments.$.state':'维修中'}}
                    )
        dormitorynotice_collection.update_one({"OnlyID":OnlyID},{"$set":{"State":State,"Dealtime":Dealtime}})
        return jsonify("处理成功"),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400
    
# 调换宿舍处理(同一宿舍内调换)
@admin_bp.route('/adminSwap', methods=['POST'])
@jwt_required()
def adminAgreeChange():
    try:
        data = request.get_json()
        current_user = get_jwt_identity()
        account = data['account']
        OnlyID = data['OnlyID']
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        StudentA_id = data['StudentA_id']
        StudentB_id = data['StudentB_id'] 
        if StudentA_id is None or StudentB_id is None:
            raise Exception("参数缺少")
        dormA = mydormitory_collection.find_one({"roommatesinfo.StudentID":StudentA_id})
        dormB = mydormitory_collection.find_one({"roommatesinfo.StudentID":StudentB_id})
        if dormA is None or dormB is None:
            raise Exception("宿舍不存在")
        StudentA = next((s for s in dormA['roommatesinfo'] if s['StudentID'] == StudentA_id), None)
        StudentB = next((s for s in dormB['roommatesinfo'] if s['StudentID'] == StudentB_id), None)

        if StudentA is None or StudentB is None:
            raise Exception("错误3:学生不存在")
        
        # 同宿舍对调
        if dormA['DormitoryID'] == dormB['DormitoryID']:
            resultA = mydormitory_collection.update_one(
            {"DormitoryID":dormA['DormitoryID'],"roommatesinfo.BedNumber":StudentA['BedNumber']},
            {
                "$set":{
                    "roommatesinfo.$.StudentID":StudentB_id,
                    "roommatesinfo.$.Name":StudentB['Name'],
                    "roommatesinfo.$.Professional":StudentB['Professional'],
                    "roommatesinfo.$.Class":StudentB['Class'],
                    "roommatesinfo.$.phone":StudentB['phone'],
                }
            }
            )
            resultB = mydormitory_collection.update_one(
            {"DormitoryID":dormA['DormitoryID'],"roommatesinfo.BedNumber":StudentB['BedNumber']},
            {
                "$set":{
                    "roommatesinfo.$.StudentID":StudentA_id,
                    "roommatesinfo.$.Name":StudentA['Name'],
                    "roommatesinfo.$.Professional":StudentA['Professional'],
                    "roommatesinfo.$.Class":StudentA['Class'],
                    "roommatesinfo.$.phone":StudentA['phone'],
                }
            }
            )
            stu_collection.update_one({"account":StudentA_id},{"$set":{"BedNumber":StudentB['BedNumber']}})
            stu_collection.update_one({"account":StudentB_id},{"$set":{"BedNumber":StudentA['BedNumber']}})
            if resultA.modified_count == 0 and resultB.modified_count == 0:
                raise Exception("错误4:调换失败")
        else:
            # 跨宿舍调换
            # 先将A换到B
            resultA = mydormitory_collection.update_one(
                {"DormitoryID":dormA['DormitoryID'],"roommatesinfo.BedNumber":StudentA['BedNumber']}, 
                {
                    "$set":{
                        "roommatesinfo.$.StudentID":StudentB_id,
                        "roommatesinfo.$.Name":StudentB['Name'],
                        "roommatesinfo.$.Professional":StudentB['Professional'],
                        "roommatesinfo.$.Class":StudentB['Class'],
                        "roommatesinfo.$.phone":StudentB['phone'],
                    } 
                }
            )
            # 再将B换到A
            resultB = mydormitory_collection.update_one(
                {"DormitoryID":dormB['DormitoryID'],"roommatesinfo.BedNumber":StudentB['BedNumber']},
                {
                        "$set":{
                        "roommatesinfo.$.StudentID":StudentA_id,
                        "roommatesinfo.$.Name":StudentA['Name'],
                        "roommatesinfo.$.Professional":StudentA['Professional'],
                        "roommatesinfo.$.Class":StudentA['Class'],
                        "roommatesinfo.$.phone":StudentA['phone'],
                    } 
                } 
            )
            # 更换学生的宿舍ID和床号
            stu_collection.update_one({"account":StudentA_id},{"$set":{"BedNumber":StudentB['BedNumber']}})
            stu_collection.update_one({"account":StudentA_id},{"$set":{"DormitoryID":StudentB['DormitoryID']}})

            stu_collection.update_one({"account":StudentB_id},{"$set":{"BedNumber":StudentA['BedNumber']}})
            stu_collection.update_one({"account":StudentB_id},{"$set":{"DormitoryID":StudentA['DormitoryID']}})

            if resultA.modified_count == 0 and resultB.modified_count == 0:
                raise Exception("错误4:调换失败")

        Applytime = datetime.now().strftime("%Y-%m-%d %H:%M")
        dormitorynotice_collection.update_one({"OnlyID":OnlyID},{"$set":{"State":'已处理','Applytime':Applytime}})
        return jsonify("处理成功"),200
    except Exception as e:
        return jsonify("发生异常", str(e)),400

# 调换到空床位
@admin_bp.route('/adminChange', methods=['POST'])
@jwt_required()
def adminChange():
    try:
        data = request.get_json()
        current_user = get_jwt_identity()
        account = data['account']
        OnlyID = data['OnlyID']
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        StudentA_id = data['StudentA_id']
        Target_id = data['Target_id']
        Empty_Bed = data['Empty_Bed']
        if StudentA_id is None or Target_id is None or Empty_Bed is None:
            raise Exception("参数缺少")
        
        dormA = mydormitory_collection.find_one({"roommatesinfo.StudentID":StudentA_id})
        dormB = mydormitory_collection.find_one({"DormitorID":Target_id})
        Bed = dormB['roommatesinfo']
        if dormA is None or dormB is None:
            raise Exception("宿舍不存在")
        StudentA = next((s for s in dormA['roommatesinfo'] if s['StudentID'] == StudentA_id), None)
        for item in Bed:
            if item['BedNumber'] == Empty_Bed:
                if item['StudentID'] is not None:
                    raise Exception("错误2:该床位已被占")
        mydormitory_collection.update_one(
            {
            "DormitoryID":Target_id,"roommatesinfo.BedNumber":Empty_Bed
            },
            {
            "$set":{
                "roommatesinfo.$.StudentID":StudentA_id,
                "roommatesinfo.$.Name":StudentA['Name'],
                "roommatesinfo.$.Professional":StudentA['Professional'],
                "roommatesinfo.$.Class":StudentA['Class'],
                "roommatesinfo.$.phone":StudentA['phone'],
            }
            }
            )
        stu_collection.update_one({"account":StudentA_id},{"$set":{"BedNumber":Empty_Bed}})
        if Target_id != dormA["DormitoryID"]:
            stu_collection.update_one({"account":StudentA_id},{"$set":{"DormitoryID":Target_id}})
        Applytime = datetime.now().strftime("%Y-%m-%d %H:%M")
        dormitorynotice_collection.update_one({"OnlyID":OnlyID},{"$set":{"State":'已处理','Applytime':Applytime}})
        return jsonify("处理成功"),200
    except Exception as e:
        return jsonify("发生异常", str(e)),400

             
# 查看单个宿舍申请
@admin_bp.route('/checkDormApply', methods=['POST'])
@jwt_required()
def dormNotice():
    try:
        data = request.get_json()
        current_user = get_jwt_identity()
        account = data['account']
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        OnlyID = data['OnlyID']
        notice = dormitorynotice_collection.find_one({"OnlyID":OnlyID},{'_id':0})
        if notice is None:
            raise Exception("错误2:通知不存在")
        return jsonify(notice),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400
    
#  查看全部宿舍申请
@admin_bp.route('/allDormApply', methods=['POST'])
@jwt_required()
def allDormNotice():
    try:
        current_user = get_jwt_identity()
        account = request.get_json()['account']
        Title = request.get_json()['Title']
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        notices = dormitorynotice_collection.find({'Title':Title},{'_id':0})
        notices_list = list(notices)
        return jsonify(notices_list),200        
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
        Time = datetime.now().strftime("%Y-%m-%d %H:%M")
        if Publisher is None or Title is None or Content is None:
            raise Exception("参数缺少")
        Noticeid = notice_collection.count_documents({})+1
        notice_collection.insert_one({"Noticeid":str(Noticeid),"Publisher":Publisher,"Title":Title,"Content":Content,"Time":Time})
        return jsonify("发布成功"),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400

# 修改宿舍通知
@admin_bp.route('/updateInfo', methods=['POST'])
@jwt_required()
def updateInfo():
    try:
        data = request.get_json()
        current_user = get_jwt_identity()
        account = data['account']
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        Noticeid = data['Noticeid']
        Title = data['Title']
        Content = data['Content']
        Time = datetime.now().strftime("%Y-%m-%d %H:%M")
        if Noticeid is None or Title is None or Content is None:
            raise Exception("参数缺少")
        notice_collection.update_one({"Noticeid":Noticeid},{"$set":{"Title":Title,"Content":Content,"Time":Time}})
        return jsonify("修改成功"),200
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
        noticeid = data['Noticeid']
        if noticeid is None:
            raise Exception("参数缺少")
        notice_collection.delete_one({"Noticeid":noticeid})
        return jsonify("删除成功"),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400
    
# 查看单个宿舍通知
@admin_bp.route('/notice', methods=['POST'])
@jwt_required()
def notice():
    try:
        data = request.get_json()
        account = data['account']
        Noticeid = data['Noticeid']
        current_user = get_jwt_identity()
        if check_identity(current_user,account) == False:
            raise Exception('当前用户错误')
        if account is None or Noticeid is None:
            raise Exception('缺少参数')
        notice = notice_collection.find_one({'Noticeid':Noticeid},{'_id':0})
        return jsonify(notice),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400
    
# 查看全部宿舍通知
@admin_bp.route('/allNotice', methods=['POST'])
@jwt_required()
def allNotice():
    try:
        current_user = get_jwt_identity()
        account = request.get_json()['account']
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        notices = notice_collection.find({},{'_id':0})
        notices_list = list(notices)
        return jsonify(notices_list),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400
    
# 查看单个宿舍
@admin_bp.route('/dormitoryInfo', methods=['POST'])
@jwt_required()
def dormitoryInfo():
    try:
        data = request.get_json()
        account = data['account']
        DormitoryID = data['DormitoryID']
        if account is None or DormitoryID is None:
            raise Exception("参数缺少")
        current_user = get_jwt_identity()
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        dormitory = mydormitory_collection.find_one({"DormitoryID":DormitoryID},{"_id":0})
        return jsonify(dormitory),200
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
        VisitorID = data['VisitorID']
        adminState =  data['adminState']
        Applytime = datetime.now().strftime("%Y-%m-%d %H:%M")
        Dealtime = datetime.now().strftime("%Y-%m-%d %H:%M")
        if VisitorID is None:
            raise Exception ("参数缺少")
        visitor_collection.update_one({"VisitorID":VisitorID},{"$set":{"adminState":adminState,"Applytime":Applytime,'Dealtime':Dealtime}})
        return jsonify({"message":"处理成功"}),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400

# 单个访客
@admin_bp.route('/Visitor', methods=['POST'])
@jwt_required()
def Visitor():
    try:
        data = request.get_json()
        current_user = get_jwt_identity()
        account = data['account']
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        VisitorID = data['VisitorID']
        if VisitorID is None:
            raise Exception("参数缺少")
        visitor = visitor_collection.find_one({"VisitorID":VisitorID},{"_id":0})
        if visitor is None:
            raise Exception('访客不存在')
        return jsonify(visitor),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400
    
# 全部访客
@admin_bp.route('/allVisitors',  methods=['POST'])
@jwt_required()
def allVisitors():
    try:
        current_user = get_jwt_identity()
        account = request.get_json()['account']
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        visitors = visitor_collection.find({},{"_id":0})
        visitors_list = list(visitors)
        return jsonify(visitors_list),200
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
        stu_collection.insert_one({"account":StudentID,"password":password,"Role":"user","DormitoryBuilding":Building,"DormitoryID":DormitoryID,"BedNumber":BedNumber,"BaseInfo":BaseInfo,"EducationInfo":EducationInfo,})
        return jsonify({"message":"添加成功"}),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400
    
# 修改学生信息
@admin_bp.route('/updateStudent', methods=['POST'])
@jwt_required()
def updateStudent():
    try:
        data = request.get_json()
        current_user = get_jwt_identity()
        account = data['account']
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        StudentID = data['StudentID']
        Building = data['Building']
        DormitoryID = data['DormitoryID']
        BedNumber = data['BedNumber']
        Name = data['Name']
        Counselor = data['Counselor']
        CounselorPhoneNumber = data['CounselorPhoneNumber']
        GraduationStatus = data['GraduationStatus']
        Faculty = data['Faculty']
        Professional = data['Professional']
        Grade = data['Grade']
        Class = data['Class']
        Duration = data['Duration']
        EnrollmentDate = data['EnrollmentDate']
        GraduationDate = data['GraduationDate']
        if GraduationStatus is None or Faculty is None or Professional is None or Grade is None or Class is None or Duration is None or EnrollmentDate is None or StudentID is None or Counselor is None or CounselorPhoneNumber is None  or Building is None or DormitoryID is None or BedNumber is None or account is None or GraduationDate is None:
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
        stu_collection.update_one({"account":StudentID},{"$set":{"DormitoryBuilding":Building,"DormitoryID":DormitoryID,"BedNumber":BedNumber,"BaseInfo":BaseInfo,"EducationInfo":EducationInfo,}})
        return jsonify({"message":"修改成功"}),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400
    
# 删除学生
@admin_bp.route('/deleteStudent', methods=['POST'])
@jwt_required()
def deleteStudent():
    try:
        data = request.get_json()
        account = data['account']
        StudentID = data['StudentID']
        if account is None or StudentID is None:
            raise Exception("参数缺少")
        current_user = get_jwt_identity()
        if check_identity(current_user, account) == False:
            raise Exception("当前用户错误")
        stu_collection.delete_one({"account":StudentID})
        mydormitory_collection.delete_one({"roommatesinfo.StudenID":StudentID})
        return jsonify({"message":"删除成功"}),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400
    
# 查看单个学生信息
@admin_bp.route('/studentInfo', methods=['POST'])
@jwt_required()
def studentInfo():
    try:
        data = request.get_json()
        account = data['account']
        StudentID = data['StudentID']
        if account is None or StudentID is None:
            raise Exception("参数缺少")
        current_user = get_jwt_identity()
        if check_identity(current_user,account) == False:
            raise Exception("当前用户错误")
        student = stu_collection.find_one({"account":StudentID},{"_id":0,"password":0})
        if student is None:
            raise Exception("学生不存在")
        return jsonify(student),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400

# 查看所有学生
@admin_bp.route('/allStudentInfo', methods = ['POST'])
@jwt_required()
def allStudentInfo():
    try:
        current_user = get_jwt_identity()
        account = request.get_json()['account']
        if check_identity(current_user,account) == False:
            raise Exception("错误1:用户错误")
        students = stu_collection.find({},{"_id":0,"BaseInfo":1,"EducationInfo":1})
        students_list = list(students)
        return jsonify(students_list),200
    except Exception as e:
        return jsonify("发生异常",str(e)),400
