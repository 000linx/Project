from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity, verify_jwt_in_request
)
from flask_principal import (
    Principal, Identity, RoleNeed,
    Permission, identity_changed, identity_loaded
)
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import timedelta

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

jwt = JWTManager(app)
Principal(app)

# 模拟用户数据库
users = {
    'admin': {
        'password_hash': generate_password_hash('adminpassword'),
        'roles': ['admin']
    }
}

# JWT 身份加载回调
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return Identity(identity)

# 在 before_request 钩子中安全加载身份
@app.before_request
def load_identity():
    try:
        verify_jwt_in_request(optional=True)  # 允许未认证请求
        current_user = get_jwt_identity()
        if current_user:
            identity = Identity(current_user)
            identity_changed.send(app, identity=identity)
    except Exception as e:
        print(f"JWT 验证失败: {e}")

# 权限加载回调
@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    if identity.id and identity.id in users:
        user = users[identity.id]
        identity.provides.update([RoleNeed(role) for role in user['roles']])

# 定义管理员权限
admin_permission = Permission(RoleNeed('admin'))

# 管理员路由（正确装饰器顺序）
@app.route('/admin')
@jwt_required()
@admin_permission.require()
def admin():
    current_user = get_jwt_identity()
    return jsonify(msg=f"Welcome, {current_user}"), 200

# 登录路由（无需 JWT 验证）
@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify(msg="请求必须为 JSON 格式"), 400

    username = request.json.get('username', '')
    password = request.json.get('password', '')

    user = users.get(username)
    if user and check_password_hash(user['password_hash'], password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200

    return jsonify(msg="用户名或密码错误"), 401

if __name__ == '__main__':
    app.run(debug=True, port=4000)