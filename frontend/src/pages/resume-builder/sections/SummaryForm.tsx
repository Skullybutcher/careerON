
import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { resumeSectionService } from '@/services/api';
import { Summary } from '@/types';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';
import { Save } from 'lucide-react';

const summarySchema = z.object({
  content: z
    .string()
    .min(10, 'Summary should be at least 10 characters')
    .max(1000, 'Summary should be less than 1000 characters'),
});

type SummaryFormValues = z.infer<typeof summarySchema>;

interface SummaryFormProps {
  resumeId: string | undefined;
}

export function SummaryForm({ resumeId }: SummaryFormProps) {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [initialData, setInitialData] = useState<Summary | null>(null);

  const form = useForm<SummaryFormValues>({
    resolver: zodResolver(summarySchema),
    defaultValues: {
      content: '',
    },
  });

  useEffect(() => {
    const fetchSummary = async () => {
      if (!resumeId) return;
      
      try {
        setIsLoading(true);
        const response = await fetch(`https://api.careernavigator.example.com/api/v1/resumes/${resumeId}/sections/summary`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });
        
        if (response.ok) {
          const data = await response.json();
          setInitialData(data);
          
          // Set form values
          form.reset({
            content: data.content || '',
          });
        }
      } catch (error) {
        console.error('Error fetching summary:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSummary();
  }, [resumeId, form]);

  const onSubmit = async (data: SummaryFormValues) => {
    if (!resumeId) return;
    
    try {
      setIsLoading(true);
      await resumeSectionService.updateSection(resumeId, 'summary', data);
      
      toast({
        title: 'Summary saved',
        description: 'Your professional summary has been updated successfully',
      });
    } catch (error) {
      console.error('Error saving summary:', error);
      toast({
        title: 'Save failed',
        description: 'There was an error saving your summary',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Professional Summary</h2>
      
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="content"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Summary</FormLabel>
                <FormControl>
                  <Textarea 
                    placeholder="Write a concise summary of your professional background, skills, and career goals..." 
                    className="min-h-[200px]"
                    {...field} 
                    disabled={isLoading} 
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          
          <div className="flex justify-between items-center">
            <p className="text-sm text-gray-500">
              Character count: {form.watch('content')?.length || 0}/1000
            </p>
            
            <Button 
              type="submit" 
              className="bg-brand-600 hover:bg-brand-700" 
              disabled={isLoading}
            >
              <Save className="mr-2 h-4 w-4" />
              {isLoading ? 'Saving...' : 'Save Summary'}
            </Button>
          </div>
        </form>
      </Form>
    </div>
  );
}
