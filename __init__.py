from datetime import timedelta
from flask import Flask
from utils import blacklist
from flask_cors import CORS
from stu_module import stu_bp
from admin_module import admin_bp
from flask_jwt_extended import JWTManager
# from test import test_bp

app = Flask(__name__)
app.register_blueprint(stu_bp)
app.register_blueprint(admin_bp)
# app.register_blueprint(test_bp)

# JWT配置
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_SECRET_KEY'] = 'linx000' 
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
jwt = JWTManager(app)



@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in blacklist
CORS(app)

if __name__ == '__main__':
    app.run(port=4000)
