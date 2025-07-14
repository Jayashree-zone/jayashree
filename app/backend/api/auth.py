from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from extensions import db
from models.user import User
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Rate limiter (attach to app in main.py)
limiter = Limiter(key_func=get_remote_address)

def is_password_complex(password):
    return (
        len(password) >= 8 and
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"[0-9]", password) and
        re.search(r"[^A-Za-z0-9]", password)
    )

@auth_bp.route('/signup', methods=['POST'])
@limiter.limit("5 per minute")
def signup():
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not name or not email or not password:
        return jsonify({'message': 'All fields are required.'}), 400
    if not is_password_complex(password):
        return jsonify({'message': 'Password not complex enough.'}), 400
    if User.query.filter((User.username == name) | (User.email == email)).first():
        return jsonify({'message': 'Username or email already exists.'}), 400

    hashed_password = generate_password_hash(password)
    user = User(username=name, email=email, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created successfully.'}), 201

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.get_json()
    identifier = data.get('username', '') or data.get('email', '')
    password = data.get('password', '')

    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid credentials.'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({
        'token': access_token,
        'user': {'id': user.id, 'username': user.username, 'email': user.email}
    }), 200 