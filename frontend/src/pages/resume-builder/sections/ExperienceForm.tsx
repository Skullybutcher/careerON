import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { resumeSectionService } from '../../../services/api';
import { Experience } from '../../../types';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '../../../components/ui/form';
import { Input } from '../../../components/ui/input';
import { Textarea } from '../../../components/ui/textarea';
import { Button } from '../../../components/ui/button';
import { Card, CardContent } from '../../../components/ui/card';
import { Checkbox } from '../../../components/ui/checkbox';
import { useToast } from '../../../components/ui/use-toast';
import { Plus, Save, Trash, Edit } from 'lucide-react';

const experienceSchema = z.object({
  company: z.string().min(1, 'Company name is required'),
  position: z.string().min(1, 'Position is required'),
  location: z.string().min(1, 'Location is required'),
  start_date: z.string().min(1, 'Start date is required'),
  end_date: z.string().optional(),
  current: z.boolean().default(false),
  description: z.string().min(1, 'Description is required'),
  achievements: z.array(z.string()).optional(),
});

type ExperienceFormValues = z.infer<typeof experienceSchema>;

interface ExperienceFormProps {
  resumeId: string | undefined;
  onSaveSuccess?: () => void;
}

export function ExperienceForm({ resumeId, onSaveSuccess }: ExperienceFormProps) {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [experiences, setExperiences] = useState<Experience[]>([]);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [isAdding, setIsAdding] = useState(false);
  const [achievementInput, setAchievementInput] = useState('');

  const form = useForm<ExperienceFormValues>({
    resolver: zodResolver(experienceSchema),
    defaultValues: {
      company: '',
      position: '',
      location: '',
      start_date: '',
      end_date: '',
      current: false,
      description: '',
      achievements: [],
    },
  });

  useEffect(() => {
    const fetchExperience = async () => {
      if (!resumeId) return;
      
      try {
        setIsLoading(true);
        const data = await resumeSectionService.getSection(resumeId, 'experience');
        if (Array.isArray(data)) {
          setExperiences(data);
        } else {
          setExperiences([]);
        }
      } catch (error) {
        console.error('Error fetching experience:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchExperience();
  }, [resumeId]);

  const watchCurrent = form.watch('current');
  
  useEffect(() => {
    // If current job is selected, clear end date
    if (watchCurrent) {
      form.setValue('end_date', '');
    }
  }, [watchCurrent, form]);

  const onSubmit = async (data: ExperienceFormValues) => {
    if (!resumeId) return;
    
    try {
      setIsLoading(true);
      
      const updatedExperiences = [...experiences];
      
      // Ensure data has all the required properties for Experience type
      const experienceData: Experience = {
        company: data.company,
        position: data.position,
        location: data.location,
        start_date: data.start_date,
        end_date: data.end_date,
        current: data.current,
        description: data.description,
        achievements: data.achievements
      };
      
      if (editingIndex !== null) {
        // Update existing experience
        updatedExperiences[editingIndex] = experienceData;
      } else {
        // Add new experience
        updatedExperiences.push(experienceData);
      }
      
      await resumeSectionService.updateSection(resumeId, 'experience', updatedExperiences);
      
      setExperiences(updatedExperiences);
      setEditingIndex(null);
      setIsAdding(false);
      
      form.reset({
        company: '',
        position: '',
        location: '',
        start_date: '',
        end_date: '',
        current: false,
        description: '',
        achievements: [],
      });
      
      toast({
        title: 'Experience saved',
        description: editingIndex !== null ? 'Experience entry updated successfully' : 'New experience entry added successfully',
      });
      if (onSaveSuccess) {
        onSaveSuccess();
      }
    } catch (error) {
      console.error('Error saving experience:', error);
      toast({
        title: 'Save failed',
        description: 'There was an error saving your experience information',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleEdit = (index: number) => {
    const experience = experiences[index];
    form.reset({
      company: experience.company,
      position: experience.position,
      location: experience.location,
      start_date: experience.start_date,
      end_date: experience.end_date || '',
      current: experience.current,
      description: experience.description,
      achievements: experience.achievements || [],
    });
    setEditingIndex(index);
    setIsAdding(true);
  };

  const handleDelete = async (index: number) => {
    if (!resumeId) return;
    
    try {
      setIsLoading(true);
      
      const updatedExperiences = [...experiences];
      updatedExperiences.splice(index, 1);
      
      await resumeSectionService.updateSection(resumeId, 'experience', updatedExperiences);
      
      setExperiences(updatedExperiences);
      
      toast({
        title: 'Experience deleted',
        description: 'Experience entry removed successfully',
      });
      if (onSaveSuccess) {
        onSaveSuccess();
      }
    } catch (error) {
      console.error('Error deleting experience:', error);
      toast({
        title: 'Delete failed',
        description: 'There was an error deleting your experience entry',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddNew = () => {
    form.reset({
      company: '',
      position: '',
      location: '',
      start_date: '',
      end_date: '',
      current: false,
      description: '',
      achievements: [],
    });
    setEditingIndex(null);
    setIsAdding(true);
  };

  const handleCancel = () => {
    setIsAdding(false);
    setEditingIndex(null);
    form.reset();
  };

  const handleAddAchievement = () => {
    if (achievementInput.trim()) {
      const currentAchievements = form.getValues('achievements') || [];
      form.setValue('achievements', [...currentAchievements, achievementInput.trim()]);
      setAchievementInput('');
    }
  };

  const handleRemoveAchievement = (index: number) => {
    const currentAchievements = form.getValues('achievements') || [];
    const newAchievements = [...currentAchievements];
    newAchievements.splice(index, 1);
    form.setValue('achievements', newAchievements);
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Work Experience</h2>
        {!isAdding && (
          <Button 
            onClick={handleAddNew}
            className="bg-brand-600 hover:bg-brand-700"
            disabled={isLoading}
          >
            <Plus className="mr-2 h-4 w-4" />
            Add Experience
          </Button>
        )}
      </div>
      
      {isAdding ? (
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="company"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Company Name</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="Company/Organization Name" 
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
                name="position"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Position/Title</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="Your job title" 
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
                        placeholder="City, State, Country or Remote" 
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
                name="current"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
                    <FormControl>
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={field.onChange}
                        disabled={isLoading}
                      />
                    </FormControl>
                    <div className="space-y-1 leading-none">
                      <FormLabel>Current Position</FormLabel>
                    </div>
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
              
              {!watchCurrent && (
                <FormField
                  control={form.control}
                  name="end_date"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>End Date</FormLabel>
                      <FormControl>
                        <Input 
                          type="date"
                          {...field} 
                          disabled={isLoading || watchCurrent} 
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              )}
            </div>
            
            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Job Description</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Describe your responsibilities and contributions..."
                      className="resize-none"
                      {...field}
                      disabled={isLoading}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <div className="space-y-2">
              <FormLabel>Key Achievements (Optional)</FormLabel>
              
              <div className="flex space-x-2">
                <Input
                  placeholder="Add an achievement or key accomplishment"
                  value={achievementInput}
                  onChange={(e) => setAchievementInput(e.target.value)}
                  disabled={isLoading}
                />
                <Button 
                  type="button"
                  onClick={handleAddAchievement}
                  disabled={isLoading || !achievementInput.trim()}
                >
                  Add
                </Button>
              </div>
              
              <div className="space-y-2 mt-2">
                {form.watch('achievements')?.map((achievement, index) => (
                  <div key={index} className="flex items-center justify-between bg-gray-50 p-2 rounded">
                    <span className="text-sm">{achievement}</span>
                    <Button 
                      type="button" 
                      variant="ghost" 
                      size="sm"
                      onClick={() => handleRemoveAchievement(index)}
                      disabled={isLoading}
                    >
                      <Trash className="h-4 w-4 text-red-500" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>
            
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
                {isLoading ? 'Saving...' : editingIndex !== null ? 'Update Experience' : 'Add Experience'}
              </Button>
            </div>
          </form>
        </Form>
      ) : (
        <>
          {experiences.length === 0 ? (
            <div className="text-center py-8 border border-dashed rounded-lg">
              <p className="text-gray-500 mb-4">No work experience entries added yet</p>
              <Button 
                onClick={handleAddNew}
                variant="outline"
              >
                <Plus className="mr-2 h-4 w-4" />
                Add Your First Experience
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {experiences.map((experience, index) => (
                <Card key={index}>
                  <CardContent className="p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-medium">{experience.position}</h3>
                        <p>{experience.company} - {experience.location}</p>
                        <p className="text-sm text-gray-500">
                          {new Date(experience.start_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short' })} - 
                          {experience.current ? ' Present' : experience.end_date ? new Date(experience.end_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short' }) : ''}
                        </p>
                        <p className="mt-2 text-sm">{experience.description}</p>
                        
                        {experience.achievements && experience.achievements.length > 0 && (
                          <div className="mt-2">
                            <p className="text-sm font-medium">Key Achievements:</p>
                            <ul className="text-sm list-disc list-inside">
                              {experience.achievements.map((achievement, i) => (
                                <li key={i}>{achievement}</li>
                              ))}
                            </ul>
                          </div>
                        )}
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
