import { useState, useEffect } from 'react';
import { resumeService, resumeSectionService } from '../../services/api';
import { Resume, PersonalInfo, Summary, Education, Experience, Skill, Project } from '../../types';

interface ResumePreviewProps {
  resumeId: string | undefined;
}

export function ResumePreview({ resumeId }: ResumePreviewProps) {
  const [resume, setResume] = useState<Resume | null>(null);
  const [personalInfo, setPersonalInfo] = useState<PersonalInfo | null>(null);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [education, setEducation] = useState<Education[]>([]);
  const [experience, setExperience] = useState<Experience[]>([]);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchResumeData = async () => {
    if (!resumeId) return;

    try {
      setIsLoading(true);

      // Fetch resume details
      const resumeData = await resumeService.getResumeDetails(resumeId);
      setResume(resumeData);

      // Fetch sections
      try {
        const personalInfoData = await resumeSectionService.getSection(resumeId, 'personal_info');
        setPersonalInfo(personalInfoData);
      } catch (error) {
        console.error('Error fetching personal info:', error);
      }

      try {
        const summaryData = await resumeSectionService.getSection(resumeId, 'summary');
        setSummary({ content: summaryData.summary });
      } catch (error) {
        console.error('Error fetching summary:', error);
      }

      try {
        const educationData = await resumeSectionService.getSection(resumeId, 'education');
        if (Array.isArray(educationData)) {
          setEducation(educationData);
        }
      } catch (error) {
        console.error('Error fetching education:', error);
      }

      try {
        const experienceData = await resumeSectionService.getSection(resumeId, 'experience');
        if (Array.isArray(experienceData)) {
          setExperience(experienceData);
        }
      } catch (error) {
        console.error('Error fetching experience:', error);
      }

      try {
        const skillsData = await resumeSectionService.getSection(resumeId, 'skills');
        if (Array.isArray(skillsData)) {
          setSkills(skillsData);
        }
      } catch (error) {
        console.error('Error fetching skills:', error);
      }

      try {
        const projectsData = await resumeSectionService.getSection(resumeId, 'projects');
        if (Array.isArray(projectsData)) {
          setProjects(projectsData);
        }
      } catch (error) {
        console.error('Error fetching projects:', error);
      }
    } catch (error) {
      console.error('Error fetching resume data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchResumeData();
  }, [resumeId]);

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-brand-400 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="font-sans text-gray-900 max-w-4xl mx-auto p-6">
      {/* Header / Personal Info */}
      <header className="mb-6">
        <h1 className="text-3xl font-bold text-center text-brand-800 mb-2">
          {personalInfo?.full_name || 'Your Name'}
        </h1>
        
        <div className="text-center text-gray-600 text-sm space-y-1">
          {personalInfo?.email && (
            <p>{personalInfo.email}</p>
          )}
          
          {personalInfo?.phone && (
            <p>{personalInfo.phone}</p>
          )}
          
          {personalInfo?.location && (
            <p>{personalInfo.location}</p>
          )}
          
          <div className="flex justify-center space-x-4 mt-2">
            {personalInfo?.linkedin_url && (
              <a href={personalInfo.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-brand-600 hover:underline">
                LinkedIn
              </a>
            )}
            
            {personalInfo?.github_url && (
              <a href={personalInfo.github_url} target="_blank" rel="noopener noreferrer" className="text-brand-600 hover:underline">
                GitHub
              </a>
            )}
            
            {personalInfo?.portfolio_url && (
              <a href={personalInfo.portfolio_url} target="_blank" rel="noopener noreferrer" className="text-brand-600 hover:underline">
                Portfolio
              </a>
            )}
          </div>
        </div>
      </header>
      
      {/* Summary */}
      {summary?.content && (
        <section className="mb-6">
          <h2 className="text-xl font-bold border-b-2 border-gray-200 pb-1 mb-3">
            Professional Summary
          </h2>
          <p className="text-gray-700">
            {summary.content}
          </p>
        </section>
      )}
      
      {/* Experience */}
      {experience.length > 0 && (
        <section className="mb-6">
          <h2 className="text-xl font-bold border-b-2 border-gray-200 pb-1 mb-3">
            Work Experience
          </h2>
          
          <div className="space-y-4">
            {experience.map((job, index) => (
              <div key={index} className="mb-3">
                <div className="flex justify-between items-baseline">
                  <h3 className="text-lg font-semibold">{job.position}</h3>
                  <span className="text-sm text-gray-600">
                    {new Date(job.start_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short' })} - 
                    {job.current ? ' Present' : job.end_date ? new Date(job.end_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short' }) : ''}
                  </span>
                </div>
                
                <div className="text-gray-800">{job.company} | {job.location}</div>
                
                <p className="text-gray-700 mt-2">{job.description}</p>
                
                {job.achievements && job.achievements.length > 0 && (
                  <ul className="list-disc list-inside mt-2 text-gray-700">
                    {job.achievements.map((achievement, i) => (
                      <li key={i}>{achievement}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </section>
      )}
      
      {/* Education */}
      {education.length > 0 && (
        <section className="mb-6">
          <h2 className="text-xl font-bold border-b-2 border-gray-200 pb-1 mb-3">
            Education
          </h2>
          
          <div className="space-y-4">
            {education.map((edu, index) => (
              <div key={index} className="mb-3">
                <div className="flex justify-between items-baseline">
                  <h3 className="text-lg font-semibold">{edu.institution}</h3>
                  <span className="text-sm text-gray-600">
                    {new Date(edu.start_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short' })} - 
                    {edu.end_date ? new Date(edu.end_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short' }) : ' Present'}
                  </span>
                </div>
                
                <div className="text-gray-800">
                  {edu.degree} in {edu.field_of_study}
                  {edu.gpa && ` | GPA: ${edu.gpa}`}
                </div>
                
                {edu.description && (
                  <p className="text-gray-700 mt-2">{edu.description}</p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}
      
      {/* Skills */}
      {skills.length > 0 && (
        <section className="mb-6">
          <h2 className="text-xl font-bold border-b-2 border-gray-200 pb-1 mb-3">
            Skills
          </h2>
          
          <div className="flex flex-wrap gap-2">
            {skills.map((skill, index) => (
              <span 
                key={index} 
                className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm"
                title={`${skill.proficiency} | ${skill.years_of_experience || 0} years`}
              >
                {skill.name}
              </span>
            ))}
          </div>
        </section>
      )}
      
      {/* Projects */}
      {projects.length > 0 && (
        <section className="mb-6">
          <h2 className="text-xl font-bold border-b-2 border-gray-200 pb-1 mb-3">
            Projects
          </h2>
          
          <div className="space-y-4">
            {projects.map((project, index) => (
              <div key={index} className="mb-3">
                <div className="flex justify-between items-baseline">
                  <h3 className="text-lg font-semibold">
                    {project.title}
                    {project.url && (
                      <a href={project.url} target="_blank" rel="noopener noreferrer" className="text-sm text-brand-600 hover:underline ml-2">
                        (View Project)
                      </a>
                    )}
                  </h3>
                  <span className="text-sm text-gray-600">
                    {new Date(project.start_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short' })} - 
                    {project.end_date ? new Date(project.end_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short' }) : ' Present'}
                  </span>
                </div>
                
                <p className="text-gray-700 mt-2">{project.description}</p>
                
                <div className="flex flex-wrap gap-1 mt-2">
                  {project.technologies.map((tech, i) => (
                    <span key={i} className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded text-xs">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}