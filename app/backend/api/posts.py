import os
import time
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models.post import Post
from models.user import User
from extensions import db

posts_bp = Blueprint('posts', __name__, url_prefix='/api/posts')

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'mp4', 'mov', 'avi'}
UPLOAD_SUBDIR = 'post_media'
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB limit

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_media_filename(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    timestamp = int(time.time())
    return f"{timestamp}_{secure_filename(filename)}"

@posts_bp.route('/', methods=['POST'])
@login_required
def create_post():
    """Create a new post"""
    data = request.get_json()
    
    if not data or not data.get('content'):
        return jsonify({'error': 'Post content is required'}), 400
    
    content = data['content'].strip()
    if len(content) > 1000:
        return jsonify({'error': 'Post content too long (max 1000 characters)'}), 400
    
    # Create post
    post = Post(
        user_id=current_user.id,
        content=content,
        media_url=data.get('media_url'),
        media_type=data.get('media_type')
    )
    
    try:
        db.session.add(post)
        db.session.commit()
        
        # Get user info for response
        user = User.query.get(current_user.id)
        
        return jsonify({
            'message': 'Post created successfully',
            'post': {
                'id': post.id,
                'content': post.content,
                'media_url': post.media_url,
                'media_type': post.media_type,
                'created_at': post.created_at.isoformat(),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'avatar_url': user.avatar_url
                },
                'likes_count': 0,
                'is_liked': False
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create post'}), 500

@posts_bp.route('/', methods=['GET'])
@login_required
def get_posts():
    """Get all posts with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    posts_data = []
    for post in posts.items:
        user = User.query.get(post.user_id)
        # Check if current user liked this post
        is_liked = post.likes.filter_by(user_id=current_user.id).first() is not None
        
        posts_data.append({
            'id': post.id,
            'content': post.content,
            'media_url': post.media_url,
            'media_type': post.media_type,
            'created_at': post.created_at.isoformat(),
            'user': {
                'id': user.id,
                'username': user.username,
                'avatar_url': user.avatar_url
            },
            'likes_count': post.likes.count(),
            'is_liked': is_liked
        })
    
    return jsonify({
        'posts': posts_data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': posts.total,
            'pages': posts.pages,
            'has_next': posts.has_next,
            'has_prev': posts.has_prev
        }
    }), 200

@posts_bp.route('/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    """Like or unlike a post"""
    post = Post.query.get_or_404(post_id)
    
    # Check if user already liked the post
    existing_like = post.likes.filter_by(user_id=current_user.id).first()
    
    if existing_like:
        # Unlike
        db.session.delete(existing_like)
        action = 'unliked'
    else:
        # Like
        from models.post import PostLike
        like = PostLike(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        action = 'liked'
    
    try:
        db.session.commit()
        return jsonify({
            'message': f'Post {action} successfully',
            'likes_count': post.likes.count(),
            'is_liked': action == 'liked'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update like'}), 500

@posts_bp.route('/media', methods=['POST'])
@login_required
def upload_media():
    """Upload media for posts"""
    UPLOAD_FOLDER = os.path.join(current_app.root_path, '..', 'uploads', UPLOAD_SUBDIR)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    if 'media' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['media']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if file_size > MAX_CONTENT_LENGTH:
        return jsonify({'error': 'File too large. Maximum 10MB allowed'}), 400

    filename = secure_media_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    
    try:
        file.save(save_path)
        
        # Determine media type
        ext = filename.rsplit('.', 1)[1].lower()
        media_type = 'video' if ext in ['mp4', 'mov', 'avi'] else 'image'
        
        return jsonify({
            'media_url': f"/api/posts/uploads/{filename}",
            'media_type': media_type,
            'filename': filename
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to save media'}), 500

@posts_bp.route('/uploads/<filename>')
def serve_media(filename):
    """Serve uploaded media files"""
    UPLOAD_FOLDER = os.path.join(current_app.root_path, '..', 'uploads', UPLOAD_SUBDIR)
    return send_from_directory(UPLOAD_FOLDER, filename) 