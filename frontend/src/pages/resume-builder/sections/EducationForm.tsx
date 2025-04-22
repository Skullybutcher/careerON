
import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { resumeSectionService } from '@/services/api';
import { Education } from '@/types';
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
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import { Plus, Save, Trash, Edit } from 'lucide-react';

const educationSchema = z.object({
  institution: z.string().min(1, 'Institution name is required'),
  degree: z.string().min(1, 'Degree is required'),
  field_of_study: z.string().min(1, 'Field of study is required'),
  start_date: z.string().min(1, 'Start date is required'),
  end_date: z.string().optional(),
  gpa: z.coerce.number().min(0).max(4.0).optional(),
  description: z.string().max(500, 'Description must be less than 500 characters').optional(),
});

type EducationFormValues = z.infer<typeof educationSchema>;

interface EducationFormProps {
  resumeId: string | undefined;
}

export function EducationForm({ resumeId }: EducationFormProps) {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [educations, setEducations] = useState<Education[]>([]);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [isAdding, setIsAdding] = useState(false);

  const form = useForm<EducationFormValues>({
    resolver: zodResolver(educationSchema),
    defaultValues: {
      institution: '',
      degree: '',
      field_of_study: '',
      start_date: '',
      end_date: '',
      gpa: undefined,
      description: '',
    },
  });

  useEffect(() => {
    const fetchEducation = async () => {
      if (!resumeId) return;
      
      try {
        setIsLoading(true);
        const data = await resumeSectionService.getSection(resumeId, 'education');
        if (Array.isArray(data)) {
          setEducations(data);
        } else {
          setEducations([]);
        }
      } catch (error) {
        console.error('Error fetching education:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchEducation();
  }, [resumeId]);

  const onSubmit = async (data: EducationFormValues) => {
    if (!resumeId) return;
    
    try {
      setIsLoading(true);
      
      const updatedEducations = [...educations];
      
      // Ensure data has all the required properties for Education type
      const educationData: Education = {
        institution: data.institution,
        degree: data.degree,
        field_of_study: data.field_of_study,
        start_date: data.start_date,
        end_date: data.end_date,
        gpa: data.gpa,
        description: data.description
      };
      
      if (editingIndex !== null) {
        // Update existing education
        updatedEducations[editingIndex] = educationData;
      } else {
        // Add new education
        updatedEducations.push(educationData);
      }
      
      await resumeSectionService.updateSection(resumeId, 'education', updatedEducations);
      
      setEducations(updatedEducations);
      setEditingIndex(null);
      setIsAdding(false);
      
      form.reset({
        institution: '',
        degree: '',
        field_of_study: '',
        start_date: '',
        end_date: '',
        gpa: undefined,
        description: '',
      });
      
      toast({
        title: 'Education saved',
        description: editingIndex !== null ? 'Education entry updated successfully' : 'New education entry added successfully',
      });
    } catch (error) {
      console.error('Error saving education:', error);
      toast({
        title: 'Save failed',
        description: 'There was an error saving your education information',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleEdit = (index: number) => {
    const education = educations[index];
    form.reset({
      institution: education.institution,
      degree: education.degree,
      field_of_study: education.field_of_study,
      start_date: education.start_date,
      end_date: education.end_date || '',
      gpa: education.gpa,
      description: education.description || '',
    });
    setEditingIndex(index);
    setIsAdding(true);
  };

  const handleDelete = async (index: number) => {
    if (!resumeId) return;
    
    try {
      setIsLoading(true);
      
      const updatedEducations = [...educations];
      updatedEducations.splice(index, 1);
      
      await resumeSectionService.updateSection(resumeId, 'education', updatedEducations);
      
      setEducations(updatedEducations);
      
      toast({
        title: 'Education deleted',
        description: 'Education entry removed successfully',
      });
    } catch (error) {
      console.error('Error deleting education:', error);
      toast({
        title: 'Delete failed',
        description: 'There was an error deleting your education entry',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddNew = () => {
    form.reset({
      institution: '',
      degree: '',
      field_of_study: '',
      start_date: '',
      end_date: '',
      gpa: undefined,
      description: '',
    });
    setEditingIndex(null);
    setIsAdding(true);
  };

  const handleCancel = () => {
    setIsAdding(false);
    setEditingIndex(null);
    form.reset();
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Education</h2>
        {!isAdding && (
          <Button 
            onClick={handleAddNew}
            className="bg-brand-600 hover:bg-brand-700"
            disabled={isLoading}
          >
            <Plus className="mr-2 h-4 w-4" />
            Add Education
          </Button>
        )}
      </div>
      
      {isAdding ? (
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="institution"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Institution</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="University/College Name" 
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
                name="degree"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Degree</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="Bachelor's, Master's, etc." 
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
                name="field_of_study"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Field of Study</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="Computer Science, Business, etc." 
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
                name="gpa"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>GPA (Optional)</FormLabel>
                    <FormControl>
                      <Input 
                        type="number"
                        step="0.01"
                        min="0"
                        max="4.0"
                        placeholder="e.g., 3.8" 
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
                name="start_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Start Date</FormLabel>
                    <FormControl>
                      <Input 
                        type="date"
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
                name="end_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>End Date (or Expected)</FormLabel>
                    <FormControl>
                      <Input 
                        type="date"
                        {...field} 
                        disabled={isLoading} 
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            
            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description (Optional)</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Describe coursework, achievements, projects, or other notable aspects of your education..."
                      className="resize-none"
                      {...field}
                      disabled={isLoading}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <div className="flex justify-end space-x-2">
              <Button
                type="button"
                variant="outline"
                onClick={handleCancel}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                className="bg-brand-600 hover:bg-brand-700"
                disabled={isLoading}
              >
                <Save className="mr-2 h-4 w-4" />
                {isLoading ? 'Saving...' : editingIndex !== null ? 'Update Education' : 'Add Education'}
              </Button>
            </div>
          </form>
        </Form>
      ) : (
        <>
          {educations.length === 0 ? (
            <div className="text-center py-8 border border-dashed rounded-lg">
              <p className="text-gray-500 mb-4">No education entries added yet</p>
              <Button 
                onClick={handleAddNew}
                variant="outline"
              >
                <Plus className="mr-2 h-4 w-4" />
                Add Your First Education
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {educations.map((education, index) => (
                <Card key={index}>
                  <CardContent className="p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-medium">{education.institution}</h3>
                        <p>{education.degree} in {education.field_of_study}</p>
                        <p className="text-sm text-gray-500">
                          {new Date(education.start_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short' })} - 
                          {education.end_date ? new Date(education.end_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short' }) : ' Present'}
                        </p>
                        {education.gpa && <p className="text-sm">GPA: {education.gpa}</p>}
                        {education.description && <p className="mt-2 text-sm">{education.description}</p>}
                      </div>
                      <div className="flex space-x-2">
                        <Button 
                          variant="ghost" 
                          size="icon"
                          onClick={() => handleEdit(index)}
                          disabled={isLoading}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="icon"
                          onClick={() => handleDelete(index)}
                          disabled={isLoading}
                        >
                          <Trash className="h-4 w-4 text-red-500" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
