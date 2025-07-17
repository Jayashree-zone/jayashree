import os
import time
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models.user import User
from models.profile import Profile, Skill, Experience, Education
from extensions import db

profile_bp = Blueprint('profile', __name__, url_prefix='/api/profile')

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
UPLOAD_SUBDIR = 'profile_images'
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB limit

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_image_filename(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    timestamp = int(time.time())
    return f"{timestamp}_{secure_filename(filename)}"

@profile_bp.route('/', methods=['GET'])
@login_required
def get_profile():
    """Get current user's profile"""
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    
    skills = Skill.query.filter_by(profile_id=profile.id).all()
    experiences = Experience.query.filter_by(profile_id=profile.id).all()
    educations = Education.query.filter_by(profile_id=profile.id).all()
    
    return jsonify({
        'profile': {
            'id': profile.id,
            'user_id': profile.user_id,
            'bio': profile.bio,
            'skills': [{'id': s.id, 'name': s.name} for s in skills],
            'experiences': [{
                'id': e.id, 
                'company': e.company, 
                'role': e.role, 
                'years': e.years
            } for e in experiences],
            'educations': [{
                'id': e.id, 
                'institution': e.institution, 
                'degree': e.degree, 
                'year': e.year
            } for e in educations]
        }
    }), 200

@profile_bp.route('/', methods=['PUT'])
@login_required
def update_profile():
    """Update current user's profile"""
    data = request.get_json()
    
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.session.add(profile)
    
    # Update basic profile info
    if 'bio' in data:
        profile.bio = data['bio'][:256] if data['bio'] else None
    
    # Update skills
    if 'skills' in data:
        # Remove existing skills
        Skill.query.filter_by(profile_id=profile.id).delete()
        # Add new skills
        for skill_data in data['skills']:
            if skill_data.get('name'):
                skill = Skill(
                    profile_id=profile.id,
                    name=skill_data['name'][:64]
                )
                db.session.add(skill)
    
    # Update experiences
    if 'experiences' in data:
        # Remove existing experiences
        Experience.query.filter_by(profile_id=profile.id).delete()
        # Add new experiences
        for exp_data in data['experiences']:
            if exp_data.get('company') and exp_data.get('role'):
                experience = Experience(
                    profile_id=profile.id,
                    company=exp_data['company'][:128],
                    role=exp_data['role'][:128],
                    years=exp_data.get('years')
                )
                db.session.add(experience)
    
    # Update educations
    if 'educations' in data:
        # Remove existing educations
        Education.query.filter_by(profile_id=profile.id).delete()
        # Add new educations
        for edu_data in data['educations']:
            if edu_data.get('institution') and edu_data.get('degree'):
                education = Education(
                    profile_id=profile.id,
                    institution=edu_data['institution'][:128],
                    degree=edu_data['degree'][:128],
                    year=edu_data.get('year')
                )
                db.session.add(education)
    
    try:
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update profile'}), 500

@profile_bp.route('/image', methods=['POST'])
@login_required
def upload_profile_image():
    """Upload profile image"""
    UPLOAD_FOLDER = os.path.join(current_app.root_path, '..', 'uploads', UPLOAD_SUBDIR)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only JPG, JPEG, PNG allowed'}), 400
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if file_size > MAX_CONTENT_LENGTH:
        return jsonify({'error': 'File too large. Maximum 5MB allowed'}), 400

    filename = secure_image_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    
    try:
        file.save(save_path)
        
        user = User.query.get(current_user.id)
        user.avatar_url = f"/api/profile/uploads/{filename}"
        db.session.commit()

        return jsonify({'image_url': user.avatar_url}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to save image'}), 500

@profile_bp.route('/uploads/<filename>')
def serve_profile_image(filename):
    """Serve uploaded profile images"""
    UPLOAD_FOLDER = os.path.join(current_app.root_path, '..', 'uploads', UPLOAD_SUBDIR)
    return send_from_directory(UPLOAD_FOLDER, filename)

@profile_bp.route('/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    """Get profile of any user by ID"""
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    skills = Skill.query.filter_by(profile_id=profile.id).all()
    experiences = Experience.query.filter_by(profile_id=profile.id).all()
    educations = Education.query.filter_by(profile_id=profile.id).all()
    
    return jsonify({
        'profile': {
            'id': profile.id,
            'user_id': profile.user_id,
            'bio': profile.bio,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'avatar_url': user.avatar_url
            },
            'skills': [{'id': s.id, 'name': s.name} for s in skills],
            'experiences': [{
                'id': e.id, 
                'company': e.company, 
                'role': e.role, 
                'years': e.years
            } for e in experiences],
            'educations': [{
                'id': e.id, 
                'institution': e.institution, 
                'degree': e.degree, 
                'year': e.year
            } for e in educations]
        }
    }), 200 