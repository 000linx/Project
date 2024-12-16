from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from stu_module import stu_bp
from admin_module import admin_bp
from flask_jwt_extended import JWTManager
from test import test_bp

app = Flask(__name__)
app.register_blueprint(stu_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(test_bp)

# 配置JWT, 过期时间为1小时
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1) 
app.config['JWT_SECRET_KEY'] = 'linx000' 
jwt = JWTManager(app)

CORS(app)

if __name__ == '__main__':
    app.run(port=4000)
