import os
import time
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.backend.models.user import User
from app.backend.extensions import db

profile_bp = Blueprint('profile', __name__, url_prefix='/api/profile')

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
UPLOAD_SUBDIR = 'profile_images'

# Ensure upload directory exists
UPLOAD_FOLDER = os.path.join(current_app.root_path, '..', 'uploads', UPLOAD_SUBDIR)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set max file size (5MB)
MAX_CONTENT_LENGTH = 5 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_image_filename(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    timestamp = int(time.time())
    return f"{timestamp}_{secure_filename(filename)}"

@profile_bp.route('/image', methods=['POST'])
@login_required
def upload_profile_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    if file.content_length and file.content_length > MAX_CONTENT_LENGTH:
        return jsonify({'error': 'File too large'}), 400

    filename = secure_image_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    user = User.query.get(current_user.id)
    user.avatar_url = f"/api/profile/uploads/{filename}"
    db.session.commit()

    return jsonify({'image_url': user.avatar_url}), 200

@profile_bp.route('/uploads/<filename>')
@login_required
def serve_profile_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename) 