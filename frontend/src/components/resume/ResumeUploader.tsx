
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { resumeService, resumeSectionService } from '@/services/api';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Upload, FileText, Check } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

export function ResumeUploader() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [open, setOpen] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type === 'application/pdf') {
        setFile(selectedFile);
      } else {
        toast({
          title: 'Invalid file type',
          description: 'Please upload a PDF file',
          variant: 'destructive',
        });
      }
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === 'application/pdf') {
        setFile(droppedFile);
      } else {
        toast({
          title: 'Invalid file type',
          description: 'Please upload a PDF file',
          variant: 'destructive',
        });
      }
    }
  };

  const handleUpload = async () => {
    if (!file || !user?.id) return;
    
    try {
      setIsUploading(true);
      
      // 1. Parse the resume
      const parsedData = await resumeService.parseResume(file);
      
      // 2. Create a new resume
      const resumeData = {
        user_id: user.id,
        title: file.name.replace('.pdf', '') || 'Imported Resume',
        summary: parsedData.personal_info?.summary || '',
        section_settings: [
          { name: 'personal_info', visible: true, order: 1 },
          { name: 'summary', visible: true, order: 2 },
          { name: 'education', visible: true, order: 3 },
          { name: 'experience', visible: true, order: 4 },
          { name: 'skills', visible: true, order: 5 },
        ],
      };
      
      const newResume = await resumeService.createResume(resumeData);
      
      // 3. Update each section with the parsed data
      if (parsedData.personal_info) {
        await resumeSectionService.updateSection(newResume.id, 'personal_info', parsedData.personal_info);
      }
      
      if (parsedData.education && parsedData.education.length > 0) {
        await resumeSectionService.updateSection(newResume.id, 'education', parsedData.education);
      }
      
      if (parsedData.experience && parsedData.experience.length > 0) {
        await resumeSectionService.updateSection(newResume.id, 'experience', parsedData.experience);
      }
      
      if (parsedData.skills && parsedData.skills.length > 0) {
        await resumeSectionService.updateSection(newResume.id, 'skills', parsedData.skills);
      }
      
      toast({
        title: 'Resume uploaded successfully',
        description: 'Your resume has been parsed and is ready for editing',
        variant: 'default',
      });
      
      setOpen(false);
      navigate(`/builder/${newResume.id}`);
    } catch (error) {
      console.error('Error uploading resume:', error);
      toast({
        title: 'Upload failed',
        description: 'There was an error uploading your resume',
        variant: 'destructive',
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Card className="h-full cursor-pointer border-dashed hover:border-brand-300 hover:bg-gray-50 transition-colors">
          <CardContent className="flex flex-col items-center justify-center h-full py-6">
            <Upload className="h-12 w-12 text-gray-400 mb-4" />
            <CardTitle className="text-lg font-medium text-center mb-2">Upload Existing Resume</CardTitle>
            <CardDescription className="text-center">
              Upload your PDF resume to parse and import its content
            </CardDescription>
          </CardContent>
        </Card>
      </DialogTrigger>
      
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Upload Existing Resume</DialogTitle>
          <DialogDescription>
            Upload your PDF resume to parse and import its content automatically.
          </DialogDescription>
        </DialogHeader>
        
        <div 
          className={`border-2 border-dashed rounded-lg p-6 mt-4 mb-4 flex flex-col items-center justify-center ${
            isDragging ? 'border-brand-500 bg-brand-50' : 'border-gray-300'
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {file ? (
            <div className="flex flex-col items-center">
              <div className="flex items-center justify-center w-12 h-12 rounded-full bg-green-100 mb-4">
                <Check className="h-6 w-6 text-green-600" />
              </div>
              <p className="text-sm font-medium mb-1">{file.name}</p>
              <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(2)} KB</p>
              <Button
                variant="outline"
                size="sm"
                className="mt-4"
                onClick={() => setFile(null)}
              >
                Change File
              </Button>
            </div>
          ) : (
            <>
              <FileText className="h-12 w-12 text-gray-400 mb-4" />
              <p className="text-sm text-center mb-2">
                Drag & drop your PDF resume here, or click to browse
              </p>
              <p className="text-xs text-gray-500 text-center mb-4">
                Supports PDF format only
              </p>
              <Input
                type="file"
                accept=".pdf"
                className="hidden"
                id="resume-upload"
                onChange={handleFileChange}
              />
              <label htmlFor="resume-upload">
                <Button
                  variant="outline"
                  className="cursor-pointer"
                  onClick={() => document.getElementById('resume-upload')?.click()}
                  type="button"
                >
                  Browse Files
                </Button>
              </label>
            </>
          )}
        </div>
        
        <DialogFooter>
          <Button
            onClick={handleUpload}
            disabled={!file || isUploading}
            className="w-full bg-brand-600 hover:bg-brand-700"
          >
            {isUploading ? 'Processing...' : 'Upload & Parse Resume'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
