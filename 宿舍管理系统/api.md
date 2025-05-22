# API结构汇总

## 管理端：
*管理员登录/adminLogin*
*退出登录/adminLogout*
*管理员忘记密码/adminForgetPwd*
*修改密码/adminChangePwd*
*访客处理/adminAgreeVisitor*
*单个访客/Visitor*
*全部访客/allVisitors*
*全部申请/allDormApply*
*单个申请/checkDormApply*
*申请处理/dormApply*
*删除通知/deleteNotice*
*发布通知/publishNotice*
*全部通知/allNotice*
*单个通知/notice*
*管理员信息/adminInfo*
*修改宿舍通知/updateInfo*
*添加单个学生/addStudent*
*删除单个学生/deleteStudent*
*修改学生信息/updateStudent*
*查看单个宿舍/dormitoryInfo*
*交换宿舍学生/adminSwap*
*移动到空床位/adminChange*
*查看单个学生信息/studentInfo*
*查看所有学生信息/allStudentInfo*
*重置学生密码/resetPassword*
*添加管理员/addAdmin*
*删除管理员/deleteAdmin*
*更改管理员信息/updateAdmin*
*管理员信息/adminInfo*
*查看全部管理员/checkAllAdmin*
*查看单个管理员/checkAdmin*
*重置管理员密码/resetAdminPassword*

## 学生端：
*学生信息查询//StuInfo*
*更新学生信息/StuUpdateInfo*
*学生所有通知/StuAllNotices*
*学生单个通知/StuNotice*
*学生所有申请/StuallDormApply*
*学生单个申请/Stuapply*
*报修申请/StuRepairApply*
*报修确认/StuRepairConfirm*
*学生撤销申请/StuCancelApple*
*学生宿舍信息/StuDormitory*
*学生更换宿舍/StuExchangeDormitory*
*学生申请退宿/StuQuitDormitory*
*学生假期留宿//StuStayDormitory*
*同意换宿申请/StuAgreeExchange*
*单个访客信息/StuVisitor*
*全部访客记录/StuVisitors*
*学生访客申请/StuApplyVisitor*
*取消访问申请/StuCancelVisitor*
*访客申请处理/StuAgreeVisitor*
*学生登录/StuLogin*
*退出登录/StuLogout*
*学生忘记密码/StuForgetPwd*
*修改密码/StuChangePwd*

## 公共端：
*宿舍总览/allDorm*
*发送邮件/sendEmail*
*查找学生/findStudent*
*验证验证码/verify_code*


# 管理端（Admin）
## 原接口	规范化后	HTTP Method	说明
/adminLogin	/auth/admin/login	POST	管理员登录
/adminLogout	/auth/admin/logout	POST	退出登录
/adminForgetPwd	/auth/admin/forgot-password	POST	忘记密码
/adminChangePwd	/auth/admin/change-password	PUT	修改密码
/adminAgreeVisitor	/visitors/{id}/approve	PUT	审批访客
/Visitor	/visitors/{id}	GET	获取单个访客详情
/allVisitors	/visitors	GET	分页获取所有访客
/allDormApply	/applications/dorm	GET	获取所有宿舍申请
/checkDormApply	/applications/dorm/{id}	GET	查看单个申请详情
/dormApply	/applications/dorm/{id}/process	PUT	处理申请
/deleteNotice	/notices/{id}	DELETE	删除通知
/publishNotice	/notices	POST	发布通知
/allNotice	/notices	GET	分页获取所有通知
/notice	/notices/{id}	GET	获取单个通知
/adminInfo	/admins/{id}	GET	获取管理员信息
/updateInfo	/dormitories/{id}/notices	PUT	更新宿舍通知
/addStudent	/students	POST	添加学生
/deleteStudent	/students/{id}	DELETE	删除学生
/updateStudent	/students/{id}	PUT	修改学生信息
/dormitoryInfo	/dormitories/{id}	GET	查看宿舍详情
/adminSwap	/dormitories/swap	POST	交换学生床位
/adminChange	/dormitories/{id}/move	POST	移动到空床位
/studentInfo	/students/{id}	GET	查看学生详情
/allStudentInfo	/students	GET	分页获取所有学生
/resetPassword	/students/{id}/reset-password	PUT	重置学生密码
/addAdmin	/admins	POST	添加管理员
/deleteAdmin	/admins/{id}	DELETE	删除管理员
/updateAdmin	/admins/{id}	PUT	修改管理员信息
/checkAllAdmin	/admins	GET	获取所有管理员
/checkAdmin	/admins/{id}	GET	获取单个管理员
/resetAdminPassword	/admins/{id}/reset-password	PUT	重置管理员密码

# 学生端（Student）
## 原接口	规范化后	HTTP Method	说明
/StuInfo	/students/me	GET	获取当前学生信息
/StuUpdateInfo	/students/me	PUT	更新学生信息
/StuAllNotices	/notices	GET	分页获取通知
/StuNotice	/notices/{id}	GET	查看单个通知
/StuallDormApply	/applications/dorm	GET	获取自己的宿舍申请
/Stuapply	/applications/dorm	POST	提交宿舍申请
/StuRepairApply	/repairs	POST	提交报修申请
/StuRepairConfirm	/repairs/{id}/confirm	PUT	确认维修完成
/StuCancelApple	/applications/{id}	DELETE	撤销申请
/StuDormitory	/students/me/dormitory	GET	查看自己宿舍信息
/StuExchangeDormitory	/applications/dorm/exchange	POST	申请换宿
/StuQuitDormitory	/applications/dorm/quit	POST	申请退宿
/StuStayDormitory	/applications/holiday-stay	POST	假期留宿申请
/StuAgreeExchange	/applications/exchange/{id}/approve	PUT	同意换宿申请
/StuVisitor	/visitors/{id}	GET	查看单个访客
/StuVisitors	/visitors	GET	分页获取访客记录
/StuApplyVisitor	/visitors	POST	提交访客申请
/StuCancelVisitor	/visitors/{id}	DELETE	取消访客申请
/StuAgreeVisitor	/visitors/{id}/approve	PUT	审批访客申请
/StuLogin	/auth/student/login	POST	学生登录
/StuLogout	/auth/student/logout	POST	退出登录
/StuForgetPwd	/auth/student/forgot-password	POST	忘记密码
/StuChangePwd	/auth/student/change-password	PUT	修改密码


# 公共端（Common）
## 原接口	规范化后	HTTP Method	说明
/allDorm	/dormitories	GET	分页获取宿舍列表
/sendEmail	/utils/send-email	POST	发送邮件
/findStudent	/students/search	GET	搜索学生
/verify_code	/auth/verify-code	POST	验证码校验