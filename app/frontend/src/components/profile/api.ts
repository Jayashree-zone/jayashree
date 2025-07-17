const API_URL = 'http://localhost:5000';

export interface ProfileData {
  bio?: string;
  skills?: Array<{ id?: number; name: string }>;
  experiences?: Array<{
    id?: number;
    company: string;
    role: string;
    years?: number;
  }>;
  educations?: Array<{
    id?: number;
    institution: string;
    degree: string;
    year?: number;
  }>;
}

export interface ProfileResponse {
  profile: {
    id: number;
    user_id: number;
    bio: string | null;
    user?: {
      id: number;
      username: string;
      email: string;
      avatar_url: string | null;
    };
    skills: Array<{ id: number; name: string }>;
    experiences: Array<{
      id: number;
      company: string;
      role: string;
      years: number | null;
    }>;
    educations: Array<{
      id: number;
      institution: string;
      degree: string;
      year: number | null;
    }>;
  };
}

export const profileApi = {
  getProfile: async (): Promise<ProfileResponse> => {
    const response = await fetch(`${API_URL}/api/profile`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });
    if (!response.ok) {
      throw new Error('Failed to fetch profile');
    }
    return response.json();
  },

  getUserProfile: async (userId: number): Promise<ProfileResponse> => {
    const response = await fetch(`${API_URL}/api/profile/${userId}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });
    if (!response.ok) {
      throw new Error('Failed to fetch user profile');
    }
    return response.json();
  },

  updateProfile: async (profileData: ProfileData): Promise<{ message: string }> => {
    const response = await fetch(`${API_URL}/api/profile`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify(profileData),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to update profile');
    }
    return response.json();
  },

  uploadProfileImage: async (file: File): Promise<{ image_url: string }> => {
    const formData = new FormData();
    formData.append('image', file);

    const response = await fetch(`${API_URL}/api/profile/image`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: formData,
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to upload image');
    }
    return response.json();
  },

  getProfileImageUrl: (filename: string): string => {
    return `${API_URL}/api/profile/uploads/${filename}`;
  },
}; 