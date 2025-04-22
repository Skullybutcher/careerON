
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { resumeService } from '@/services/api';
import { Resume } from '@/types';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/components/ui/use-toast';
import { PersonalInfoForm } from './sections/PersonalInfoForm';
import { SummaryForm } from './sections/SummaryForm';
import { EducationForm } from './sections/EducationForm';
import { ExperienceForm } from './sections/ExperienceForm';
import { SkillsForm } from './sections/SkillsForm';
import { ProjectsForm } from './sections/ProjectsForm';
import { ResumePreview } from './ResumePreview';
import { ArrowLeft, Download, Save } from 'lucide-react';

export default function ResumeBuilder() {
  const { resumeId } = useParams<{ resumeId: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [resume, setResume] = useState<Resume | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('personal-info');
  const [isExporting, setIsExporting] = useState(false);

  useEffect(() => {
    const fetchResume = async () => {
      if (!resumeId) {
        navigate('/dashboard');
        return;
      }
      
      try {
        setIsLoading(true);
        const data = await resumeService.getResumeDetails(resumeId);
        setResume(data);
      } catch (err) {
        console.error('Error fetching resume:', err);
        toast({
          title: 'Error',
          description: 'Failed to load resume. Please try again.',
          variant: 'destructive',
        });
        navigate('/dashboard');
      } finally {
        setIsLoading(false);
      }
    };

    fetchResume();
  }, [resumeId, navigate, toast]);

  const handleExport = async () => {
    if (!resumeId) return;
    
    try {
      setIsExporting(true);
      const blob = await resumeService.exportResume(resumeId);
      
      // Create a download link and trigger the download
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${resume?.title || 'Resume'}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast({
        title: 'Export successful',
        description: 'Your resume has been exported as PDF',
      });
    } catch (error) {
      console.error('Error exporting resume:', error);
      toast({
        title: 'Export failed',
        description: 'Failed to export resume. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsExporting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="container px-4 py-8 mx-auto max-w-7xl">
        <div className="h-screen flex items-center justify-center">
          <div className="w-12 h-12 border-4 border-brand-400 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  if (!resume) {
    return (
      <div className="container px-4 py-8 mx-auto max-w-7xl">
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold mb-4">Resume Not Found</h2>
          <p className="text-gray-600 mb-6">The resume you're looking for doesn't exist or you don't have access to it.</p>
          <Button 
            onClick={() => navigate('/dashboard')}
            className="bg-brand-600 hover:bg-brand-700"
          >
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container px-4 py-8 mx-auto max-w-7xl">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
        <div className="flex items-center mb-4 md:mb-0">
          <Button 
            variant="ghost" 
            size="icon" 
            className="mr-2"
            onClick={() => navigate('/dashboard')}
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold">{resume.title}</h1>
            <p className="text-gray-500 text-sm">Build and customize your resume</p>
          </div>
        </div>
        <div className="flex space-x-3">
          <Button 
            variant="outline"
            onClick={handleExport}
            disabled={isExporting}
          >
            <Download className="mr-2 h-4 w-4" />
            {isExporting ? 'Exporting...' : 'Export PDF'}
          </Button>
          <Button 
            variant="default"
            className="bg-brand-600 hover:bg-brand-700"
            onClick={() => navigate(`/optimize/${resumeId}`)}
          >
            <Save className="mr-2 h-4 w-4" />
            Optimize Resume
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="w-full grid grid-cols-6">
              <TabsTrigger value="personal-info">Personal</TabsTrigger>
              <TabsTrigger value="summary">Summary</TabsTrigger>
              <TabsTrigger value="education">Education</TabsTrigger>
              <TabsTrigger value="experience">Experience</TabsTrigger>
              <TabsTrigger value="skills">Skills</TabsTrigger>
              <TabsTrigger value="projects">Projects</TabsTrigger>
            </TabsList>
            
            <div className="mt-4 border rounded-lg p-4">
              <TabsContent value="personal-info">
                <PersonalInfoForm resumeId={resumeId} />
              </TabsContent>
              
              <TabsContent value="summary">
                <SummaryForm resumeId={resumeId} />
              </TabsContent>
              
              <TabsContent value="education">
                <EducationForm resumeId={resumeId} />
              </TabsContent>
              
              <TabsContent value="experience">
                <ExperienceForm resumeId={resumeId} />
              </TabsContent>
              
              <TabsContent value="skills">
                <SkillsForm resumeId={resumeId} />
              </TabsContent>
              
              <TabsContent value="projects">
                <ProjectsForm resumeId={resumeId} />
              </TabsContent>
            </div>
          </Tabs>
        </div>
        
        <div className="border rounded-lg p-4 h-[800px] overflow-auto bg-white">
          <ResumePreview resumeId={resumeId} />
        </div>
      </div>
    </div>
  );
}
