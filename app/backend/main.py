from flask import Flask
from flask_cors import CORS
from config import Config
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from extensions import db
import os

def create_app():
    # Load environment variables
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(Config)
    # Enable CORS for local frontend ports with credentials support
    CORS(app, origins=["http://localhost:5173", "http://localhost:5174"], supports_credentials=True)
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)

    # --- Flask-Login Setup ---
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Add unauthorized handler for API endpoints
    from flask import jsonify
    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({'error': 'Unauthorized'}), 401

    # Import models after initializing db and migrate
    from models.profile import Profile, Skill, Experience, Education
    from models.post import Post, PostLike

    # Import and register blueprints
    from api.auth import auth_bp, limiter
    from api.profile import profile_bp
    from api.posts import posts_bp

    limiter.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(posts_bp)

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")
    app.run(debug=True) 