import React from "react";

interface ProfileHeaderProps {
  avatarUrl: string;
  name: string;
  title: string;
  location: string;
  socialLinks: { platform: string; url: string }[];
}

const ProfileHeader: React.FC<ProfileHeaderProps> = ({
  avatarUrl,
  name,
  title,
  location,
  socialLinks,
}) => (
  <div className="flex flex-col md:flex-row items-center bg-white shadow rounded-lg p-6 mb-4">
    <img
      src={avatarUrl}
      alt="User Avatar"
      className="w-24 h-24 rounded-full border-2 border-gray-300 mb-4 md:mb-0 md:mr-6"
    />
    <div className="flex-1 text-center md:text-left">
      <h2 className="text-2xl font-bold">{name}</h2>
      <p className="text-gray-600">{title}</p>
      <p className="text-gray-500">{location}</p>
      <div className="flex justify-center md:justify-start mt-2 space-x-3">
        {socialLinks.map((link) => (
          <a
            key={link.platform}
            href={link.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-500 hover:underline"
          >
            {link.platform}
          </a>
        ))}
      </div>
    </div>
  </div>
);

export default ProfileHeader;




