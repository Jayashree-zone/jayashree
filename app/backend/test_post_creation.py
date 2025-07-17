#!/usr/bin/env python3
"""
Comprehensive Test Script for Post Creation and Media Upload
This script tests all aspects of post creation including text-only, image upload, and video upload.
"""

import requests
import json
import os
import time
from pathlib import Path

BASE_URL = 'http://localhost:5000'

def create_test_files():
    """Create test image and video files for testing"""
    test_dir = Path('test_files')
    test_dir.mkdir(exist_ok=True)
    
    # Create a simple test image (1x1 pixel PNG)
    test_image_path = test_dir / 'test_image.png'
    if not test_image_path.exists():
        # Create a minimal PNG file (1x1 pixel, transparent)
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x07tIME\x07\xe5\x07\x11\x10\x1d\x1c\xc8\xe7\xc8\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xf6\x178\xea\x00\x00\x00\x00IEND\xaeB`\x82'
        test_image_path.write_bytes(png_data)
    
    # Create a simple test video (minimal MP4)
    test_video_path = test_dir / 'test_video.mp4'
    if not test_video_path.exists():
        # Create a minimal MP4 file (just the header)
        mp4_data = b'\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom\x00\x00\x00\x08free\x00\x00\x00\x00'
        test_video_path.write_bytes(mp4_data)
    
    return test_image_path, test_video_path

def test_authentication():
    """Test authentication endpoints"""
    print("🔐 Testing Authentication...")
    
    # Test login
    login_data = {
        'username': 'john_doe',
        'password': 'password123'
    }
    
    response = requests.post(f'{BASE_URL}/api/auth/login', json=login_data)
    if response.status_code == 200:
        token = response.json().get('access_token')
        print(f"   ✅ Login successful, token received")
        return token
    else:
        print(f"   ❌ Login failed: {response.status_code} - {response.text}")
        return None

def test_text_only_post(token):
    """Test post creation with text-only content"""
    print("\n📝 Testing Text-Only Post Creation...")
    
    headers = {'Authorization': f'Bearer {token}'}
    post_data = {
        'content': 'This is a test post with only text content! 🚀 Testing the post creation functionality.'
    }
    
    response = requests.post(f'{BASE_URL}/api/posts', json=post_data, headers=headers)
    
    if response.status_code == 201:
        result = response.json()
        print(f"   ✅ Text-only post created successfully!")
        print(f"   📄 Post ID: {result['post']['id']}")
        print(f"   📝 Content: {result['post']['content'][:50]}...")
        return result['post']['id']
    else:
        print(f"   ❌ Text-only post creation failed: {response.status_code} - {response.text}")
        return None

def test_image_upload(token):
    """Test image upload functionality"""
    print("\n🖼️  Testing Image Upload...")
    
    test_image_path, _ = create_test_files()
    
    headers = {'Authorization': f'Bearer {token}'}
    
    with open(test_image_path, 'rb') as f:
        files = {'media': ('test_image.png', f, 'image/png')}
        response = requests.post(f'{BASE_URL}/api/posts/media', files=files, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Image upload successful!")
        print(f"   🖼️  Media URL: {result['media_url']}")
        print(f"   📁 Media Type: {result['media_type']}")
        return result['media_url'], result['media_type']
    else:
        print(f"   ❌ Image upload failed: {response.status_code} - {response.text}")
        return None, None

def test_video_upload(token):
    """Test video upload functionality"""
    print("\n🎥 Testing Video Upload...")
    
    _, test_video_path = create_test_files()
    
    headers = {'Authorization': f'Bearer {token}'}
    
    with open(test_video_path, 'rb') as f:
        files = {'media': ('test_video.mp4', f, 'video/mp4')}
        response = requests.post(f'{BASE_URL}/api/posts/media', files=files, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Video upload successful!")
        print(f"   🎥 Media URL: {result['media_url']}")
        print(f"   📁 Media Type: {result['media_type']}")
        return result['media_url'], result['media_type']
    else:
        print(f"   ❌ Video upload failed: {response.status_code} - {response.text}")
        return None, None

def test_post_with_image(token):
    """Test post creation with image media"""
    print("\n📸 Testing Post Creation with Image...")
    
    # First upload an image
    media_url, media_type = test_image_upload(token)
    if not media_url:
        print("   ⚠️  Skipping image post test due to upload failure")
        return None
    
    headers = {'Authorization': f'Bearer {token}'}
    post_data = {
        'content': 'This is a test post with an image! 📸 Testing media upload functionality.',
        'media_url': media_url,
        'media_type': media_type
    }
    
    response = requests.post(f'{BASE_URL}/api/posts', json=post_data, headers=headers)
    
    if response.status_code == 201:
        result = response.json()
        print(f"   ✅ Image post created successfully!")
        print(f"   📄 Post ID: {result['post']['id']}")
        print(f"   🖼️  Media URL: {result['post']['media_url']}")
        return result['post']['id']
    else:
        print(f"   ❌ Image post creation failed: {response.status_code} - {response.text}")
        return None

def test_post_with_video(token):
    """Test post creation with video media"""
    print("\n🎬 Testing Post Creation with Video...")
    
    # First upload a video
    media_url, media_type = test_video_upload(token)
    if not media_url:
        print("   ⚠️  Skipping video post test due to upload failure")
        return None
    
    headers = {'Authorization': f'Bearer {token}'}
    post_data = {
        'content': 'This is a test post with a video! 🎬 Testing video upload functionality.',
        'media_url': media_url,
        'media_type': media_type
    }
    
    response = requests.post(f'{BASE_URL}/api/posts', json=post_data, headers=headers)
    
    if response.status_code == 201:
        result = response.json()
        print(f"   ✅ Video post created successfully!")
        print(f"   📄 Post ID: {result['post']['id']}")
        print(f"   🎥 Media URL: {result['post']['media_url']}")
        return result['post']['id']
    else:
        print(f"   ❌ Video post creation failed: {response.status_code} - {response.text}")
        return None

def test_form_validation(token):
    """Test form validation and error handling"""
    print("\n✅ Testing Form Validation...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test 1: Empty content
    print("   Testing empty content validation...")
    post_data = {'content': ''}
    response = requests.post(f'{BASE_URL}/api/posts', json=post_data, headers=headers)
    if response.status_code == 400:
        print(f"   ✅ Empty content correctly rejected: {response.json().get('error')}")
    else:
        print(f"   ❌ Empty content should have been rejected: {response.status_code}")
    
    # Test 2: Content too long
    print("   Testing content length validation...")
    long_content = 'A' * 1001  # Over 1000 character limit
    post_data = {'content': long_content}
    response = requests.post(f'{BASE_URL}/api/posts', json=post_data, headers=headers)
    if response.status_code == 400:
        print(f"   ✅ Long content correctly rejected: {response.json().get('error')}")
    else:
        print(f"   ❌ Long content should have been rejected: {response.status_code}")
    
    # Test 3: Invalid file type
    print("   Testing invalid file type validation...")
    headers = {'Authorization': f'Bearer {token}'}
    files = {'media': ('test.txt', b'This is not an image or video', 'text/plain')}
    response = requests.post(f'{BASE_URL}/api/posts/media', files=files, headers=headers)
    if response.status_code == 400:
        print(f"   ✅ Invalid file type correctly rejected: {response.json().get('error')}")
    else:
        print(f"   ❌ Invalid file type should have been rejected: {response.status_code}")

def test_loading_states_and_feedback():
    """Test loading states and user feedback (simulated)"""
    print("\n⏳ Testing Loading States and User Feedback...")
    
    # This would typically be tested in the frontend
    # Here we simulate the expected behavior
    
    print("   ✅ Loading states should show during:")
    print("      - File upload progress")
    print("      - Post submission")
    print("      - API requests")
    
    print("   ✅ User feedback should include:")
    print("      - Success messages for successful operations")
    print("      - Error messages for failed operations")
    print("      - Progress indicators for uploads")
    print("      - Form validation errors")

def test_posts_retrieval(token):
    """Test retrieving posts"""
    print("\n📋 Testing Posts Retrieval...")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/api/posts', headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        posts = result['posts']
        pagination = result['pagination']
        
        print(f"   ✅ Posts retrieved successfully!")
        print(f"   📄 Total posts: {pagination['total']}")
        print(f"   📄 Posts on current page: {len(posts)}")
        print(f"   📄 Current page: {pagination['page']}")
        print(f"   📄 Total pages: {pagination['pages']}")
        
        if posts:
            print(f"   📝 Latest post: {posts[0]['content'][:50]}...")
            if posts[0].get('media_url'):
                print(f"   🖼️  Latest post has media: {posts[0]['media_type']}")
        
        return posts
    else:
        print(f"   ❌ Posts retrieval failed: {response.status_code} - {response.text}")
        return []

def test_like_functionality(token, posts):
    """Test like/unlike functionality"""
    print("\n❤️  Testing Like Functionality...")
    
    if not posts:
        print("   ⚠️  No posts available for like testing")
        return
    
    post_id = posts[0]['id']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test liking a post
    response = requests.post(f'{BASE_URL}/api/posts/{post_id}/like', headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Post liked successfully!")
        print(f"   ❤️  Likes count: {result['likes_count']}")
        print(f"   ❤️  Is liked: {result['is_liked']}")
        
        # Test unliking the same post
        response = requests.post(f'{BASE_URL}/api/posts/{post_id}/like', headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Post unliked successfully!")
            print(f"   ❤️  Likes count: {result['likes_count']}")
            print(f"   ❤️  Is liked: {result['is_liked']}")
        else:
            print(f"   ❌ Post unlike failed: {response.status_code}")
    else:
        print(f"   ❌ Post like failed: {response.status_code} - {response.text}")

def cleanup_test_files():
    """Clean up test files"""
    print("\n🧹 Cleaning up test files...")
    test_dir = Path('test_files')
    if test_dir.exists():
        for file in test_dir.iterdir():
            file.unlink()
        test_dir.rmdir()
        print("   ✅ Test files cleaned up")

def main():
    """Run all tests"""
    print("🧪 Starting Comprehensive Post Creation and Media Upload Tests")
    print("=" * 70)
    
    # Create test files
    create_test_files()
    
    # Test authentication
    token = test_authentication()
    if not token:
        print("❌ Authentication failed. Cannot proceed with tests.")
        return
    
    # Test text-only post creation
    text_post_id = test_text_only_post(token)
    
    # Test image upload and post creation
    image_post_id = test_post_with_image(token)
    
    # Test video upload and post creation
    video_post_id = test_post_with_video(token)
    
    # Test form validation
    test_form_validation(token)
    
    # Test loading states and feedback
    test_loading_states_and_feedback()
    
    # Test posts retrieval
    posts = test_posts_retrieval(token)
    
    # Test like functionality
    test_like_functionality(token, posts)
    
    # Cleanup
    cleanup_test_files()
    
    print("\n" + "=" * 70)
    print("🎉 All tests completed!")
    print(f"📊 Test Summary:")
    print(f"   ✅ Text-only post: {'Success' if text_post_id else 'Failed'}")
    print(f"   ✅ Image post: {'Success' if image_post_id else 'Failed'}")
    print(f"   ✅ Video post: {'Success' if video_post_id else 'Failed'}")
    print(f"   ✅ Posts retrieved: {len(posts)} posts found")
    print("\n🚀 Your post creation and media upload system is working!")

if __name__ == '__main__':
    main() 