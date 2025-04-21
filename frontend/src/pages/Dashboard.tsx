
import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { resumeService } from '@/services/api';
import { Resume } from '@/types';
import { ResumeCard } from '@/components/resume/ResumeCard';
import { CreateResumeDialog } from '@/components/resume/CreateResumeDialog';
import { ResumeUploader } from '@/components/resume/ResumeUploader';
import { useToast } from '@/components/ui/use-toast';

export default function Dashboard() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchResumes = async () => {
      if (!user?.id) return;
      
      try {
        setIsLoading(true);
        const data = await resumeService.getUserResumes(user.id);
        setResumes(data);
      } catch (err) {
        console.error('Error fetching resumes:', err);
        setError('Failed to load your resumes. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchResumes();
  }, [user]);

  const handleDeleteResume = (id: string) => {
    setResumes(prevResumes => prevResumes.filter(resume => resume.id !== id));
    toast({
      title: 'Resume deleted',
      description: 'Your resume has been successfully deleted',
    });
  };

  return (
    <div className="container px-4 py-8 mx-auto max-w-7xl">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">My Resumes</h1>
          <p className="text-gray-500 mt-1">
            Manage and create your professional resumes
          </p>
        </div>
        <div className="mt-4 md:mt-0">
          <CreateResumeDialog />
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-48 rounded-lg bg-gray-100 animate-pulse" />
          ))}
        </div>
      ) : error ? (
        <div className="p-6 bg-red-50 rounded-lg border border-red-200">
          <p className="text-red-700">{error}</p>
        </div>
      ) : resumes.length === 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="h-full border rounded-lg p-6 bg-gray-50">
              <div className="flex flex-col h-full items-center justify-center text-center">
                <h2 className="text-xl font-semibold mb-2">Create Your First Resume</h2>
                <p className="text-gray-500 mb-6 max-w-md">
                  Start building your professional resume with our AI-powered resume builder.
                </p>
                <CreateResumeDialog />
              </div>
            </div>
          </div>
          <ResumeUploader />
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {resumes.map(resume => (
            <ResumeCard 
              key={resume.id} 
              resume={resume} 
              onDelete={handleDeleteResume} 
            />
          ))}
          <ResumeUploader />
        </div>
      )}
    </div>
  );
}
