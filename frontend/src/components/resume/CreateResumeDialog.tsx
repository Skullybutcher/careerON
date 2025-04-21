
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAuth } from '@/contexts/AuthContext';
import { resumeService } from '@/services/api';
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Plus } from 'lucide-react';

const createResumeSchema = z.object({
  title: z
    .string()
    .min(2, 'Title must be at least 2 characters')
    .max(100, 'Title must be less than 100 characters'),
  summary: z
    .string()
    .max(500, 'Summary must be less than 500 characters')
    .optional(),
});

type CreateResumeFormValues = z.infer<typeof createResumeSchema>;

export function CreateResumeDialog() {
  const { user, loading } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const form = useForm<CreateResumeFormValues>({
    resolver: zodResolver(createResumeSchema),
    defaultValues: {
      title: '',
      summary: '',
    },
  });

  const onSubmit = async (data: CreateResumeFormValues) => {
    console.log('User object before submission:', user);
    if (!user?.id) {
      console.error('User ID is missing. Cannot create resume.');
      return;
    }
    
    try {
      setIsLoading(true);
      const resumeData = {
        user_id: user.id,
        title: data.title,
        summary: data.summary || '',
        section_settings: [
          { name: 'personal_info', visible: true, order: 1 },
          { name: 'summary', visible: true, order: 2 },
          { name: 'education', visible: true, order: 3 },
          { name: 'experience', visible: true, order: 4 },
          { name: 'skills', visible: true, order: 5 },
          { name: 'projects', visible: true, order: 6 },
        ],
      };
      
      console.log('Creating resume with data:', resumeData);
      const newResume = await resumeService.createResume(resumeData);
      console.log('Resume created successfully:', newResume);
      if (!newResume?.id) {
        console.error('New resume ID is missing in response:', newResume);
        return;
      }
      setOpen(false);
      navigate(`/builder/${newResume.id}`);
    } catch (error) {
      console.error('Error creating resume:', error);
      alert('Failed to create resume. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="bg-brand-600 hover:bg-brand-700" disabled={loading || !user}>
          <Plus className="mr-2 h-4 w-4" />
          Create Resume
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Create New Resume</DialogTitle>
          <DialogDescription>
            Give your resume a title and optional summary to get started.
          </DialogDescription>
        </DialogHeader>
        
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 py-4">
            <FormField
              control={form.control}
              name="title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Resume Title</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="e.g., Software Developer Resume"
                      {...field}
                      disabled={isLoading}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="summary"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Summary (Optional)</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="A brief summary of your professional profile..."
                      className="resize-none"
                      {...field}
                      disabled={isLoading}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <DialogFooter>
              <Button 
                type="submit" 
                className="w-full bg-brand-600 hover:bg-brand-700" 
                disabled={isLoading}
              >
                {isLoading ? 'Creating...' : 'Create Resume'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
