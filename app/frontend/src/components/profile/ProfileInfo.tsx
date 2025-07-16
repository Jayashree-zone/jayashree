import React, { useState } from "react";

interface Experience {
  company: string;
  role: string;
  duration: string;
  description?: string;
}

interface Education {
  institution: string;
  degree: string;
  year: string;
}

interface ProfileInfoProps {
  bio: string;
  skills: string[];
  experience: Experience[];
  education: Education[];
  contact: { email: string; phone?: string; };
}

const Section: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => {
  const [open, setOpen] = useState(true);
  return (
    <div className="mb-4">
      <button
        className="w-full flex justify-between items-center font-semibold text-lg py-2 px-4 bg-gray-100 rounded hover:bg-gray-200 focus:outline-none md:cursor-default"
        onClick={() => setOpen((o) => !o)}
      >
        <span>{title}</span>
        <span>{open ? "-" : "+"}</span>
      </button>
      {open && <div className="p-4 pt-2">{children}</div>}
    </div>
  );
};

const ProfileInfo: React.FC<ProfileInfoProps> = ({ bio, skills, experience, education, contact }) => (
  <div>
    <Section title="Bio">
      <p>{bio}</p>
    </Section>
    <Section title="Skills">
      <ul className="flex flex-wrap gap-2">
        {skills.map((skill) => (
          <li key={skill} className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm">{skill}</li>
        ))}
      </ul>
    </Section>
    <Section title="Work Experience">
      <ul>
        {experience.map((exp, idx) => (
          <li key={idx} className="mb-2">
            <div className="font-semibold">{exp.role} @ {exp.company}</div>
            <div className="text-sm text-gray-500">{exp.duration}</div>
            {exp.description && <div className="text-gray-700 text-sm">{exp.description}</div>}
          </li>
        ))}
      </ul>
    </Section>
    <Section title="Education">
      <ul>
        {education.map((edu, idx) => (
          <li key={idx} className="mb-2">
            <div className="font-semibold">{edu.degree} - {edu.institution}</div>
            <div className="text-sm text-gray-500">{edu.year}</div>
          </li>
        ))}
      </ul>
    </Section>
    <Section title="Contact Information">
      <div>Email: <a href={`mailto:${contact.email}`} className="text-blue-500 underline">{contact.email}</a></div>
      {contact.phone && <div>Phone: {contact.phone}</div>}
    </Section>
  </div>
);

export default ProfileInfo; 