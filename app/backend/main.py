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
    CORS(app, origins=["http://localhost:5173", "http://localhost:5174"])
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

    @app.before_first_request
    def setup_database():
        db.create_all()
        print("✅ Database tables created successfully!")

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True) 