
import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { resumeSectionService } from '@/services/api';
import { PersonalInfo } from '@/types';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';
import { Save } from 'lucide-react';

const personalInfoSchema = z.object({
  full_name: z.string().min(1, 'Full name is required'),
  email: z.string().email('Invalid email format').min(1, 'Email is required'),
  phone: z.string().min(1, 'Phone number is required'),
  location: z.string().min(1, 'Location is required'),
  linkedin_url: z.string().url('Invalid URL format').optional().or(z.literal('')),
  github_url: z.string().url('Invalid URL format').optional().or(z.literal('')),
  portfolio_url: z.string().url('Invalid URL format').optional().or(z.literal('')),
});

type PersonalInfoFormValues = z.infer<typeof personalInfoSchema>;

interface PersonalInfoFormProps {
  resumeId: string | undefined;
}

export function PersonalInfoForm({ resumeId }: PersonalInfoFormProps) {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [initialData, setInitialData] = useState<PersonalInfo | null>(null);

  const form = useForm<PersonalInfoFormValues>({
    resolver: zodResolver(personalInfoSchema),
    defaultValues: {
      full_name: '',
      email: '',
      phone: '',
      location: '',
      linkedin_url: '',
      github_url: '',
      portfolio_url: '',
    },
  });

  useEffect(() => {
    const fetchPersonalInfo = async () => {
      if (!resumeId) return;
      
      try {
        setIsLoading(true);
        const data = await resumeSectionService.getSection(resumeId, 'personal_info');
        setInitialData(data);
        
        // Set form values
        form.reset({
          full_name: data.full_name || '',
          email: data.email || '',
          phone: data.phone || '',
          location: data.location || '',
          linkedin_url: data.linkedin_url || '',
          github_url: data.github_url || '',
          portfolio_url: data.portfolio_url || '',
        });
      } catch (error) {
        console.error('Error fetching personal info:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPersonalInfo();
  }, [resumeId, form]);

  const onSubmit = async (data: PersonalInfoFormValues) => {
    if (!resumeId) return;
    
    try {
      setIsLoading(true);
      await resumeSectionService.updateSection(resumeId, 'personal_info', data);
      
      toast({
        title: 'Personal information saved',
        description: 'Your personal information has been updated successfully',
      });
    } catch (error) {
      console.error('Error saving personal info:', error);
      toast({
        title: 'Save failed',
        description: 'There was an error saving your personal information',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Personal Information</h2>
      
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="full_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Full Name</FormLabel>
                  <FormControl>
                    <Input placeholder="John Doe" {...field} disabled={isLoading} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input 
                      type="email" 
                      placeholder="john.doe@example.com" 
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
              name="phone"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Phone</FormLabel>
                  <FormControl>
                    <Input 
                      placeholder="(123) 456-7890" 
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
              name="location"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Location</FormLabel>
                  <FormControl>
                    <Input 
                      placeholder="City, State, Country" 
                      {...field} 
                      disabled={isLoading} 
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
          
          <div className="space-y-4">
            <FormField
              control={form.control}
              name="linkedin_url"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>LinkedIn URL (Optional)</FormLabel>
                  <FormControl>
                    <Input 
                      placeholder="https://linkedin.com/in/username" 
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
              name="github_url"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>GitHub URL (Optional)</FormLabel>
                  <FormControl>
                    <Input 
                      placeholder="https://github.com/username" 
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
              name="portfolio_url"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Portfolio/Website URL (Optional)</FormLabel>
                  <FormControl>
                    <Input 
                      placeholder="https://yourportfolio.com" 
                      {...field} 
                      disabled={isLoading} 
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
          
          <Button 
            type="submit" 
            className="bg-brand-600 hover:bg-brand-700" 
            disabled={isLoading}
          >
            <Save className="mr-2 h-4 w-4" />
            {isLoading ? 'Saving...' : 'Save Information'}
          </Button>
        </form>
      </Form>
    </div>
  );
}
