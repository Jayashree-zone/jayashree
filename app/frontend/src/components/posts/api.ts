const API_URL = 'http://localhost:5000';

export interface PostData {
  content: string;
  media_url?: string;
  media_type?: string;
}

export interface Post {
  id: number;
  content: string;
  media_url?: string;
  media_type?: string;
  created_at: string;
  user: {
    id: number;
    username: string;
    avatar_url?: string;
  };
  likes_count: number;
  is_liked: boolean;
}

export interface PostsResponse {
  posts: Post[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

export const postsApi = {
  createPost: async (postData: PostData): Promise<{ message: string; post: Post }> => {
    const response = await fetch(`${API_URL}/api/posts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify(postData),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to create post');
    }
    
    return response.json();
  },

  getPosts: async (page: number = 1, perPage: number = 10): Promise<PostsResponse> => {
    const response = await fetch(`${API_URL}/api/posts?page=${page}&per_page=${perPage}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch posts');
    }
    
    return response.json();
  },

  likePost: async (postId: number): Promise<{ message: string; likes_count: number; is_liked: boolean }> => {
    const response = await fetch(`${API_URL}/api/posts/${postId}/like`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to like post');
    }
    
    return response.json();
  },

  uploadMedia: async (file: File): Promise<{ media_url: string; media_type: string; filename: string }> => {
    const formData = new FormData();
    formData.append('media', file);

    const response = await fetch(`${API_URL}/api/posts/media`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: formData,
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to upload media');
    }
    
    return response.json();
  },

  getMediaUrl: (filename: string): string => {
    return `${API_URL}/api/posts/uploads/${filename}`;
  },
}; 