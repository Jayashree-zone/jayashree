from flask import Flask
from flask_cors import CORS
from config import Config
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from extensions import db

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app, origins=["http://localhost:5173"])
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Import models after initializing db and migrate
from models.user import User
from models.profile import Profile, Skill, Experience, Education

# Import and register blueprints
from api.auth import auth_bp, limiter
limiter.init_app(app)
app.register_blueprint(auth_bp)

def setup_database():
    """Setup database tables"""
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")

# Expose 'app' at module level for Flask CLI
# (No need for create_app() unless using app factory pattern)

if __name__ == '__main__':
    setup_database()
    app.run(debug=True) 