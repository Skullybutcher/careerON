import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { resumeService } from '@/services/api';
import { Resume, OptimizationResponse } from '@/types';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/components/ui/use-toast';
import { ArrowLeft, Sparkles, AlertCircle } from 'lucide-react';

export default function ResumeOptimization() {
  const { resumeId } = useParams<{ resumeId: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [resume, setResume] = useState<Resume | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [optimizationLevel, setOptimizationLevel] = useState<'light' | 'moderate' | 'aggressive'>('moderate');
  const [isLoading, setIsLoading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [optimizationResult, setOptimizationResult] = useState<OptimizationResponse | null>(null);

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
      const result = await resumeService.optimizeResume(resumeId, jobDescription, optimizationLevel);
      setOptimizationResult(result);
      toast({
        title: 'Optimization complete',
        description: 'Your resume has been analyzed.',
      });
    } catch (error) {
      toast({
        title: 'Optimization failed',
        description: 'There was an error optimizing your resume.',
        variant: 'destructive',
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getProgressColor = (score: number) => {
    if (score >= 85) return 'bg-green-600';
    if (score >= 70) return 'bg-yellow-600';
    return 'bg-red-600';
  };

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-brand-400 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!resume) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold mb-4">Resume Not Found</h2>
        <p className="text-gray-600 mb-6">The resume you're looking for doesn't exist.</p>
        <Button onClick={() => navigate('/dashboard')}>Back to Dashboard</Button>
      </div>
    );
  }

  return (
    <div className="container px-4 py-8 mx-auto max-w-7xl">
      <div className="flex items-center mb-6">
        <Button variant="ghost" size="icon" className="mr-2" onClick={() => navigate(`/builder/${resumeId}`)}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold">Optimize Resume</h1>
          <p className="text-gray-500 text-sm">Analyze your resume against a job description</p>
        </div>
        <Button
          className="ml-auto bg-blue-600 hover:bg-blue-700 text-white"
          onClick={async () => {
            if (!resumeId) return;
            try {
              const response = await fetch(`http://localhost:5000/api/resumes/${resumeId}/export-ats?format=pdf`, {
                method: 'GET',
                headers: {
                  'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
                }
              });
              if (!response.ok) throw new Error('Failed to download PDF');
              const blob = await response.blob();
              const url = window.URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `resume_${resumeId}_ats.pdf`;
              document.body.appendChild(a);
              a.click();
              a.remove();
              window.URL.revokeObjectURL(url);
            } catch (error) {
              console.error('Error exporting ATS PDF:', error);
              alert('Failed to export ATS PDF. Please try again.');
            }
          }}
        >
          Export ATS PDF
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <Card>
            <CardContent className="p-6">
              <h2 className="text-xl font-semibold mb-4">Paste Job Description</h2>
              <Textarea
                placeholder="Paste the full job description here..."
                className="min-h-[200px] resize-none"
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                disabled={isProcessing}
              />
              <div className="mt-4 space-y-2">
                <label className="text-sm font-medium">Optimization Level</label>
                <Select
                  value={optimizationLevel}
                  onValueChange={(value) => setOptimizationLevel(value as 'light' | 'moderate' | 'aggressive')}
                  disabled={isProcessing}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select optimization level" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="light">Light</SelectItem>
                    <SelectItem value="moderate">Moderate</SelectItem>
                    <SelectItem value="aggressive">Aggressive</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button
                onClick={handleOptimize}
                className="w-full bg-brand-600 hover:bg-brand-700 mt-4"
                disabled={isProcessing || !jobDescription.trim()}
              >
                <Sparkles className="mr-2 h-4 w-4" />
                {isProcessing ? 'Analyzing...' : 'Optimize Resume'}
              </Button>
            </CardContent>
          </Card>
        </div>

        <div>
          {optimizationResult ? (
            <Card>
              <CardContent className="p-6 space-y-6">
                <h2 className="text-xl font-semibold flex items-center mb-4">
                  <Sparkles className="mr-2 h-5 w-5 text-brand-600" />
                  Optimization Results
                </h2>

                <div>
                  <div className="flex justify-between mb-2">
                    <span className="font-medium">Match Score</span>
                    <span className={`font-bold ${getScoreColor(optimizationResult.optimization.score * 100)}`}>
                      {(optimizationResult.optimization.score * 100).toFixed(2)}%
                    </span>
                  </div>
                  <Progress
                    value={optimizationResult.optimization.score * 100}
                    className={`h-2 ${getProgressColor(optimizationResult.optimization.score * 100)}`}
                  />
                  <p className="mt-2 text-sm text-gray-600">{optimizationResult.optimization.feedback}</p>
                </div>

                {optimizationResult.optimization.suggestions.length > 0 && (
                  <div>
                    <h3 className="font-medium text-lg">Improvement Suggestions</h3>
                    <ul className="space-y-2 mt-2">
                      {optimizationResult.optimization.suggestions.map((suggestion, index) => (
                        <li key={index} className="flex items-start">
                          <AlertCircle className="h-5 w-5 text-yellow-600 mr-2 mt-1" />
                          {suggestion}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="mt-6">
                  <h3 className="font-medium text-lg">Detailed Advice</h3>
                  <div className="space-y-4 text-sm text-gray-800 bg-gray-50 p-4 rounded border">
                    {optimizationResult.improvement_advice?.summary_advice && (
                      <div>
                        <strong className="block mb-1 text-gray-900">Summary:</strong>
                        <p>{optimizationResult.improvement_advice.summary_advice}</p>
                      </div>
                    )}
                    {optimizationResult.improvement_advice?.skills_advice && (
                      <div>
                        <strong className="block mb-1 text-gray-900">Skills:</strong>
                        <p>{optimizationResult.improvement_advice.skills_advice}</p>
                      </div>
                    )}
                    {optimizationResult.improvement_advice?.projects_advice && (
                      <div>
                        <strong className="block mb-1 text-gray-900">Projects:</strong>
                        <p>{optimizationResult.improvement_advice.projects_advice}</p>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="bg-gray-50 rounded-lg p-12 h-full flex flex-col items-center justify-center text-center">
              <Sparkles className="h-16 w-16 text-gray-400 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Resume Optimization</h3>
              <p className="text-gray-600 mb-6 max-w-md">
                Paste a job description on the left and click "Optimize Resume" to get tailored feedback.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
