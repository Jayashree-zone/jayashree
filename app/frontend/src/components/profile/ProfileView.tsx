import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ProfileHeader from "./ProfileHeader";
import ProfileInfo from "./ProfileInfo";

// Create a simple profile context to share data between components
interface ProfileData {
  avatarUrl: string;
  name: string;
  title: string;
  location: string;
  socialLinks: { platform: string; url: string }[];
  bio: string;
  skills: string[];
  experience: { company: string; role: string; duration: string; description?: string }[];
  education: { institution: string; degree: string; year: string }[];
  contact: { email: string; phone?: string; };
}

// Default profile data
const defaultProfile: ProfileData = {
  avatarUrl: "https://randomuser.me/api/portraits/men/32.jpg",
  name: "John Doe",
  title: "Software Engineer",
  location: "San Francisco, CA",
  socialLinks: [
    { platform: "LinkedIn", url: "https://linkedin.com/in/johndoe" },
    { platform: "GitHub", url: "https://github.com/johndoe" },
  ],
  bio: "Passionate developer with 5+ years of experience in web and mobile applications.",
  skills: ["React", "TypeScript", "Node.js", "Python"],
  experience: [
    { company: "TechCorp", role: "Frontend Developer", duration: "2019-2022", description: "Worked on scalable web apps." },
    { company: "Webify", role: "Intern", duration: "2018-2019" },
  ],
  education: [
    { institution: "Stanford University", degree: "BSc Computer Science", year: "2018" },
  ],
  contact: { email: "john.doe@email.com", phone: "123-456-7890" },
};

// Create a simple profile store using localStorage
class ProfileStore {
  private static STORAGE_KEY = 'userProfile';

  static getProfile(): ProfileData {
    const stored = localStorage.getItem(this.STORAGE_KEY);
    return stored ? JSON.parse(stored) : defaultProfile;
  }

  static updateProfile(profile: Partial<ProfileData>): void {
    const current = this.getProfile();
    const updated = { ...current, ...profile };
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(updated));
  }

  static resetProfile(): void {
    localStorage.removeItem(this.STORAGE_KEY);
  }
}

const ProfileView: React.FC = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<ProfileData>(() => ProfileStore.getProfile());

  const handleProfileUpdate = (updatedProfile: Partial<ProfileData>) => {
    ProfileStore.updateProfile(updatedProfile);
    setProfile(ProfileStore.getProfile());
  };

  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold">Profile</h1>
          <button
            onClick={() => navigate('/profile/edit', { state: { profile, onUpdate: handleProfileUpdate } })}
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Edit Profile
          </button>
        </div>
        <ProfileHeader
          avatarUrl={profile.avatarUrl}
          name={profile.name}
          title={profile.title}
          location={profile.location}
          socialLinks={profile.socialLinks}
        />
        <ProfileInfo
          bio={profile.bio}
          skills={profile.skills}
          experience={profile.experience}
          education={profile.education}
          contact={profile.contact}
        />
      </div>
    </div>
  );
};

export default ProfileView; 