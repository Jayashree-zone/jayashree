from flask import Blueprint, request, jsonify
from models.user import User, db
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    # Validation
    if not name or not email or not password or not confirm_password:
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400
    if len(password) < 8:
        return jsonify({'success': False, 'message': 'Password must be at least 8 characters.'}), 400
    if password != confirm_password:
        return jsonify({'success': False, 'message': 'Passwords do not match.'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'Email already registered.'}), 400

    hashed_password = generate_password_hash(password)
    user = User(username=name, email=email, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Signup successful!'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    # For demo, return a fake token
    return jsonify({'success': True, 'token': 'demo-token', 'message': 'Login successful!'}), 200 