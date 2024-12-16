from utils import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import get_jwt_identity,create_access_token, jwt_required
from flask import Blueprint, request, jsonify

test_bp = Blueprint('test', __name__)

stuid = "202202060222"


@test_bp.route('/login', methods=['GET'])
def login():
    access_token = create_access_token(identity=generate_identity(stuid))
    return jsonify({'message': '登录成功', 'access_token': access_token}), 200

@test_bp.route('/test', methods=['POST'])
@jwt_required()
def test():
    data = request.get_json()
    stuid = data['stuid']
    current_user = get_jwt_identity()
    if check_identity(current_user, stuid) == False:
        return jsonify({'message': '用户错误'}), 400
    
    return jsonify({'message': 'jwt验证身份成功'}), 200


