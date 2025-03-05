from datetime import timedelta
from flask import Flask
from utils import blacklist
from flask_cors import CORS
from stu_module import stu_bp
from admin_module import admin_bp
from common import common_bp
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.secret_key = "linx000"
app.register_blueprint(stu_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(common_bp)


# JWT配置
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_SECRET_KEY'] = 'linx000' 
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
jwt = JWTManager(app)


# 检查token是否在黑名单中
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in blacklist




CORS(app)

if __name__ == '__main__':
    app.run('192.168.31.55',port=4000, debug=True)
    #app.run('192.168.43.113',port=4000, debug=True)
    #app.run(port=4000, debug=True)