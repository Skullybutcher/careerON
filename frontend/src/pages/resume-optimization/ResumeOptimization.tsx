
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { resumeService } from '@/services/api';
import { Resume, OptimizationResponse } from '@/types';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/components/ui/use-toast';
import { ArrowLeft, Sparkles, CheckCircle, AlertCircle } from 'lucide-react';

export default function ResumeOptimization() {
  const { resumeId } = useParams<{ resumeId: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [resume, setResume] = useState<Resume | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [optimizationLevel, setOptimizationLevel] = useState<'light' | 'moderate' | 'aggressive'>('moderate');
  const [isLoading, setIsLoading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [optimization, setOptimization] = useState<OptimizationResponse | null>(null);

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

  const handleOptimize = async () => {
    if (!resumeId || !jobDescription.trim()) return;
    
    try {
      setIsProcessing(true);
      const result = await resumeService.optimizeResume(
        resumeId,
        jobDescription,
        optimizationLevel
      );
      
      setOptimization(result);
      
      toast({
        title: 'Optimization complete',
        description: 'Your resume has been analyzed against the job description',
      });
    } catch (error) {
      console.error('Error optimizing resume:', error);
      toast({
        title: 'Optimization failed',
        description: 'There was an error optimizing your resume',
        variant: 'destructive',
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getProgressColor = (score: number) => {
    if (score >= 80) return 'bg-green-600';
    if (score >= 60) return 'bg-yellow-600';
    return 'bg-red-600';
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
      <div className="flex items-center mb-6">
        <Button 
          variant="ghost" 
          size="icon" 
          className="mr-2"
          onClick={() => navigate(`/builder/${resumeId}`)}
        >
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold">Optimize Resume</h1>
          <p className="text-gray-500 text-sm">Analyze your resume against a job description</p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <Card>
            <CardContent className="p-6">
              <h2 className="text-xl font-semibold mb-4">Paste Job Description</h2>
              <p className="text-gray-600 mb-4">
                To optimize your resume, paste the job description you're applying for below. 
                Our AI will analyze your resume against the job requirements and provide suggestions.
              </p>
              
              <div className="space-y-4">
                <Textarea
                  placeholder="Paste the full job description here..."
                  className="min-h-[200px] resize-none"
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  disabled={isProcessing}
                />
                
                <div className="space-y-2">
                  <label className="text-sm font-medium">
                    Optimization Level
                  </label>
                  <Select
                    value={optimizationLevel}
                    onValueChange={(value) => setOptimizationLevel(value as 'light' | 'moderate' | 'aggressive')}
                    disabled={isProcessing}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select optimization level" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="light">Light - Minor suggestions</SelectItem>
                      <SelectItem value="moderate">Moderate - Balanced optimization</SelectItem>
                      <SelectItem value="aggressive">Aggressive - Comprehensive changes</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <Button 
                  onClick={handleOptimize}
                  className="w-full bg-brand-600 hover:bg-brand-700"
                  disabled={isProcessing || !jobDescription.trim()}
                >
                  <Sparkles className="mr-2 h-4 w-4" />
                  {isProcessing ? 'Analyzing Resume...' : 'Optimize Resume'}
                </Button>
              </div>
            </CardContent>
          </Card>
          
          {resume && (
            <Card>
              <CardContent className="p-6">
                <h2 className="text-xl font-semibold mb-4">Resume Details</h2>
                <div className="space-y-2">
                  <p><span className="font-medium">Title:</span> {resume.title}</p>
                  <p><span className="font-medium">Summary:</span> {resume.summary}</p>
                  <p>
                    <span className="font-medium">Last Updated:</span> {' '}
                    {new Date(resume.updated_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
        
        <div>
          {optimization ? (
            <Card>
              <CardContent className="p-6">
                <h2 className="text-xl font-semibold flex items-center mb-4">
                  <Sparkles className="mr-2 h-5 w-5 text-brand-600" />
                  Optimization Results
                </h2>
                
                <div className="mb-6">
                  <div className="flex justify-between mb-2">
                    <span className="font-medium">Match Score</span>
                    <span className={`font-bold ${getScoreColor(optimization.score)}`}>
                      {optimization.score}%
                    </span>
                  </div>
                  <Progress 
                    value={optimization.score} 
                    className={`h-2 ${getProgressColor(optimization.score)}`}
                  />
                  
                  <p className="mt-2 text-sm text-gray-600">
                    {optimization.score >= 80 
                      ? 'Your resume is well-matched to this job. Great job!'
                      : optimization.score >= 60
                        ? 'Your resume shows decent alignment. Some improvements could help.'
                        : 'Your resume needs significant improvements to match this job.'}
                  </p>
                </div>
                
                <div className="space-y-4">
                  <h3 className="font-medium text-lg">Improvement Suggestions</h3>
                  {optimization.suggestions.length > 0 ? (
                    <ul className="space-y-2">
                      {optimization.suggestions.map((suggestion, index) => (
                        <li key={index} className="flex items-start">
                          {optimization.score >= 80 ? (
                            <CheckCircle className="h-5 w-5 text-green-600 mr-2 flex-shrink-0 mt-0.5" />
                          ) : (
                            <AlertCircle className="h-5 w-5 text-yellow-600 mr-2 flex-shrink-0 mt-0.5" />
                          )}
                          <span>{suggestion}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-gray-600">
                      No specific suggestions provided. Your resume may already be well-optimized.
                    </p>
                  )}
                  
                  <div className="mt-6 pt-4 border-t border-gray-200">
                    <Button 
                      onClick={() => navigate(`/builder/${resumeId}`)}
                      className="w-full bg-brand-600 hover:bg-brand-700"
                    >
                      Apply Changes to Resume
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="bg-gray-50 rounded-lg p-12 h-full flex flex-col items-center justify-center text-center">
              <Sparkles className="h-16 w-16 text-gray-400 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Resume Optimization</h3>
              <p className="text-gray-600 mb-6 max-w-md">
                Paste a job description on the left and click "Optimize Resume" to see how well your resume matches the requirements.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
