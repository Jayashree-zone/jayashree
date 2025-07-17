#!/usr/bin/env python3
"""
Development Database Reset Script
This script resets the database by dropping all tables and recreating them with sample data.
Use this for development/testing purposes only.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, db
from models.user import User
from models.profile import Profile, Skill, Experience, Education
from models.post import Post, PostLike
from werkzeug.security import generate_password_hash

def reset_database():
    """Reset the database by dropping all tables and recreating them"""
    with app.app_context():
        print("🗑️  Dropping all tables...")
        db.drop_all()
        
        print("🏗️  Creating all tables...")
        db.create_all()
        
        print("📝 Adding sample data...")
        
        # Create sample users
        sample_users = [
            {
                'username': 'john_doe',
                'email': 'john.doe@example.com',
                'password': 'password123',
                'profile': {
                    'bio': 'Passionate developer with 5+ years of experience in web and mobile applications.',
                    'skills': ['React', 'TypeScript', 'Node.js', 'Python'],
                    'experience': [
                        {
                            'company': 'TechCorp',
                            'role': 'Frontend Developer',
                            'years': 3
                        }
                    ],
                    'education': [
                        {
                            'institution': 'Stanford University',
                            'degree': 'BSc Computer Science',
                            'year': 2018
                        }
                    ]
                }
            },
            {
                'username': 'jane_smith',
                'email': 'jane.smith@example.com',
                'password': 'password123',
                'profile': {
                    'bio': 'Experienced product manager with a focus on user-centered design and agile methodologies.',
                    'skills': ['Product Management', 'Agile', 'User Research', 'Data Analysis'],
                    'experience': [
                        {
                            'company': 'InnovateCorp',
                            'role': 'Senior Product Manager',
                            'years': 4
                        }
                    ],
                    'education': [
                        {
                            'institution': 'MIT',
                            'degree': 'MBA',
                            'year': 2020
                        }
                    ]
                }
            }
        ]
        
        for user_data in sample_users:
            # Create user
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password=generate_password_hash(user_data['password']),
                avatar_url=None  # Will be set when user uploads an image
            )
            db.session.add(user)
            db.session.flush()  # Get the user ID
            
            # Create profile
            profile_data = user_data['profile']
            profile = Profile(
                user_id=user.id,
                bio=profile_data['bio']
            )
            db.session.add(profile)
            db.session.flush()  # Get the profile ID
            
            # Add skills
            for skill_name in profile_data['skills']:
                skill = Skill(name=skill_name, profile_id=profile.id)
                db.session.add(skill)
            
            # Add experience
            for exp_data in profile_data['experience']:
                experience = Experience(
                    company=exp_data['company'],
                    role=exp_data['role'],
                    years=exp_data['years'],
                    profile_id=profile.id
                )
                db.session.add(experience)
            
            # Add education
            for edu_data in profile_data['education']:
                education = Education(
                    institution=edu_data['institution'],
                    degree=edu_data['degree'],
                    year=edu_data['year'],
                    profile_id=profile.id
                )
                db.session.add(education)
        
        # Create sample posts
        sample_posts = [
            {
                'user_id': 1,  # john_doe
                'content': 'Just finished building an amazing React application! 🚀 The new features include real-time updates, drag-and-drop functionality, and a beautiful responsive design. Can\'t wait to share more details about the tech stack we used.',
                'media_url': None,
                'media_type': None
            },
            {
                'user_id': 2,  # jane_smith
                'content': 'Excited to announce that our team just launched a new product feature that improves user engagement by 40%! 📈 The user research and iterative design process really paid off.',
                'media_url': None,
                'media_type': None
            },
            {
                'user_id': 1,  # john_doe
                'content': 'Learning TypeScript has been a game-changer for our codebase. The type safety and better IDE support make development so much more enjoyable. Highly recommend! 💻',
                'media_url': None,
                'media_type': None
            }
        ]
        
        for post_data in sample_posts:
            post = Post(**post_data)
            db.session.add(post)
        
        # Create some sample likes
        sample_likes = [
            {'user_id': 2, 'post_id': 1},  # jane likes john's first post
            {'user_id': 1, 'post_id': 2},  # john likes jane's post
            {'user_id': 2, 'post_id': 3},  # jane likes john's second post
        ]
        
        for like_data in sample_likes:
            like = PostLike(**like_data)
            db.session.add(like)
        
        # Commit all changes
        db.session.commit()
        
        print("✅ Database reset completed successfully!")
        print(f"📊 Created {len(sample_users)} sample users with profiles")
        print(f"📝 Created {len(sample_posts)} sample posts")
        print(f"❤️  Created {len(sample_likes)} sample likes")
        print("\n🔑 Sample login credentials:")
        for user_data in sample_users:
            print(f"   Username: {user_data['username']}")
            print(f"   Email: {user_data['email']}")
            print(f"   Password: {user_data['password']}")
            print()

if __name__ == '__main__':
    print("🔄 Starting database reset...")
    try:
        reset_database()
        print("🎉 Database reset completed!")
    except Exception as e:
        print(f"❌ Error during database reset: {e}")
        sys.exit(1) 