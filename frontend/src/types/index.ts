/*
  Merged file: file2 plus interfaces from file1 that were not present
*/

// User types
export interface User {
  id: string;
  name: string;
  email: string;
  created_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  name: string;
  email: string;
  password: string;
}

// Resume types
export interface Resume {
  id: string;
  user_id: string;
  title: string;
  summary: string;
  created_at: string;
  updated_at: string;
  section_settings: SectionSetting[];
}

export interface SectionSetting {
  name: string;
  visible: boolean;
  order: number;
}

export interface ResumeCreationData {
  user_id: string;
  title: string;
  summary: string;
  section_settings: SectionSetting[];
}

// Resume sections
export interface PersonalInfo {
  full_name: string;
  email: string;
  phone: string;
  location: string;
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
}

export interface Summary {
  content: string;
}

export interface Education {
  institution: string;
  degree: string;
  field_of_study: string;
  start_date: string;
  end_date?: string;
  gpa?: number;
  description?: string;
}

export interface Experience {
  company: string;
  position: string;
  location: string;
  start_date: string;
  end_date?: string;
  current: boolean;
  description: string;
  achievements?: string[];
}

export interface Skill {
  name: string;
  category: string;
  proficiency: 'beginner' | 'intermediate' | 'expert';
  years_of_experience?: number;
}

export interface Project {
  title: string;
  description: string;
  technologies: string[];
  start_date: string;
  end_date?: string;
  url?: string;
}

export interface Achievement {
  title: string;
  description: string;
  date: string;
  issuer: string;
}

export interface Extracurricular {
  activity_name: string;
  organization: string;
  role: string;
  start_date: string;
  end_date?: string;
  description?: string;
}

export interface Course {
  course_name: string;
  institution: string;
  completion_date: string;
  description?: string;
}

export interface Certification {
  name: string;
  issuing_organization: string;
  issue_date: string;
  credential_id?: string;
  credential_url?: string;
}

export interface VolunteerWork {
  organization: string;
  role: string;
  start_date: string;
  end_date?: string;
  description?: string;
}

export interface Publication {
  title: string;
  authors: string[];
  publication_venue: string;
  publication_date: string;
  url?: string;
  description?: string;
}

// Resume optimization
export interface OptimizationRequest {
  job_description: string;
  optimization_level: 'light' | 'moderate' | 'aggressive';
}

export type OptimizationResponse = {
  score: number;
  feedback: string;
  suggestions: string[];
  optimized_summary: string;
  missing_skills: string[];
  resume_boost_paragraph: string;
  summary_advice: string;
  skills_advice: string;
  projects_advice: string;
};

// Added from file1 (nested structure) - was missing in file2
export interface OptimizationResponseNested {
  optimization: {
    score: number;
    feedback: string;
    suggestions: string[];
    optimized_summary: string;
    missing_skills: string[];
    resume_boost_paragraph: string;
  };
  improvement_advice: {
    summary: string;
    skills: string;
    projects: string;
    // Add other relevant fields as needed
  };
}

// Resume parsing
export interface ParsedResume {
  personal_info: PersonalInfo;
  education?: Education[];
  experience?: Experience[];
  skills?: Skill[];
  projects?: Project[];
  achievements?: Achievement[];
  certifications?: Certification[];
  [key: string]: any;
}
