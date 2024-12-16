class Student:
    def __init__(self,faculty,name, stuid, className, phone, dormitoryid):
        self.faculty = faculty
        self.name = name
        self.stuid = stuid
        self.classname = className
        self.phone = phone
        self.dormitoryid = dormitoryid

class Admin:
    def __init__(self, name, teacherid, password, phone):
        self.name = name
        self.password = password

