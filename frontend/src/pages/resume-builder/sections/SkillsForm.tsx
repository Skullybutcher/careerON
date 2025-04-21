
import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { resumeSectionService } from '@/services/api';
import { Skill } from '@/types';
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
import { Card, CardContent } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/components/ui/use-toast';
import { Plus, Save, Trash, Edit } from 'lucide-react';

const skillSchema = z.object({
  name: z.string().min(1, 'Skill name is required'),
  category: z.string().min(1, 'Category is required'),
  proficiency: z.enum(['beginner', 'intermediate', 'expert']),
  years_of_experience: z.coerce.number().min(0).optional(),
});

type SkillFormValues = z.infer<typeof skillSchema>;

interface SkillsFormProps {
  resumeId: string | undefined;
}

export function SkillsForm({ resumeId }: SkillsFormProps) {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [isAdding, setIsAdding] = useState(false);

  const form = useForm<SkillFormValues>({
    resolver: zodResolver(skillSchema),
    defaultValues: {
      name: '',
      category: '',
      proficiency: 'intermediate',
      years_of_experience: undefined,
    },
  });

  useEffect(() => {
    const fetchSkills = async () => {
      if (!resumeId) return;
      
      try {
        setIsLoading(true);
        const response = await fetch(`https://api.careernavigator.example.com/api/v1/resumes/${resumeId}/sections/skills`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });
        
        if (response.ok) {
          const data = await response.json();
          if (Array.isArray(data)) {
            setSkills(data);
          } else {
            setSkills([]);
          }
        }
      } catch (error) {
        console.error('Error fetching skills:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSkills();
  }, [resumeId]);

  const onSubmit = async (data: SkillFormValues) => {
    if (!resumeId) return;
    
    try {
      setIsLoading(true);
      
      const updatedSkills = [...skills];
      
      // Ensure data has all the required properties for Skill type
      const skillData: Skill = {
        name: data.name,
        category: data.category,
        proficiency: data.proficiency,
        years_of_experience: data.years_of_experience
      };
      
      if (editingIndex !== null) {
        // Update existing skill
        updatedSkills[editingIndex] = skillData;
      } else {
        // Add new skill
        updatedSkills.push(skillData);
      }
      
      await resumeSectionService.updateSection(resumeId, 'skills', updatedSkills);
      
      setSkills(updatedSkills);
      setEditingIndex(null);
      setIsAdding(false);
      
      form.reset({
        name: '',
        category: '',
        proficiency: 'intermediate',
        years_of_experience: undefined,
      });
      
      toast({
        title: 'Skill saved',
        description: editingIndex !== null ? 'Skill updated successfully' : 'New skill added successfully',
      });
    } catch (error) {
      console.error('Error saving skill:', error);
      toast({
        title: 'Save failed',
        description: 'There was an error saving your skill',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleEdit = (index: number) => {
    const skill = skills[index];
    form.reset({
      name: skill.name,
      category: skill.category,
      proficiency: skill.proficiency,
      years_of_experience: skill.years_of_experience,
    });
    setEditingIndex(index);
    setIsAdding(true);
  };

  const handleDelete = async (index: number) => {
    if (!resumeId) return;
    
    try {
      setIsLoading(true);
      
      const updatedSkills = [...skills];
      updatedSkills.splice(index, 1);
      
      await resumeSectionService.updateSection(resumeId, 'skills', updatedSkills);
      
      setSkills(updatedSkills);
      
      toast({
        title: 'Skill deleted',
        description: 'Skill removed successfully',
      });
    } catch (error) {
      console.error('Error deleting skill:', error);
      toast({
        title: 'Delete failed',
        description: 'There was an error deleting your skill',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddNew = () => {
    form.reset({
      name: '',
      category: '',
      proficiency: 'intermediate',
      years_of_experience: undefined,
    });
    setEditingIndex(null);
    setIsAdding(true);
  };

  const handleCancel = () => {
    setIsAdding(false);
    setEditingIndex(null);
    form.reset();
  };

  const getProficiencyColor = (proficiency: string) => {
    switch (proficiency) {
      case 'beginner':
        return 'bg-yellow-100 text-yellow-800';
      case 'intermediate':
        return 'bg-blue-100 text-blue-800';
      case 'expert':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Skills</h2>
        {!isAdding && (
          <Button 
            onClick={handleAddNew}
            className="bg-brand-600 hover:bg-brand-700"
            disabled={isLoading}
          >
            <Plus className="mr-2 h-4 w-4" />
            Add Skill
          </Button>
        )}
      </div>
      
      {isAdding ? (
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Skill Name</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="e.g., JavaScript, Project Management, etc." 
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
                name="category"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Category</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="e.g., Programming, Design, Soft Skills" 
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
                name="proficiency"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Proficiency Level</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                      disabled={isLoading}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select proficiency level" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="beginner">Beginner</SelectItem>
                        <SelectItem value="intermediate">Intermediate</SelectItem>
                        <SelectItem value="expert">Expert</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="years_of_experience"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Years of Experience (Optional)</FormLabel>
                    <FormControl>
                      <Input 
                        type="number"
                        min="0"
                        step="0.5"
                        placeholder="e.g., 2.5" 
                        {...field} 
                        disabled={isLoading} 
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
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
                {isLoading ? 'Saving...' : editingIndex !== null ? 'Update Skill' : 'Add Skill'}
              </Button>
            </div>
          </form>
        </Form>
      ) : (
        <>
          {skills.length === 0 ? (
            <div className="text-center py-8 border border-dashed rounded-lg">
              <p className="text-gray-500 mb-4">No skills added yet</p>
              <Button 
                onClick={handleAddNew}
                variant="outline"
              >
                <Plus className="mr-2 h-4 w-4" />
                Add Your First Skill
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {skills.map((skill, index) => (
                <Card key={index}>
                  <CardContent className="p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-medium">{skill.name}</h3>
                        <p className="text-sm text-gray-500">{skill.category}</p>
                        <div className="flex items-center mt-2">
                          <span 
                            className={`text-xs px-2 py-1 rounded-full ${getProficiencyColor(skill.proficiency)}`}
                          >
                            {skill.proficiency.charAt(0).toUpperCase() + skill.proficiency.slice(1)}
                          </span>
                          {skill.years_of_experience !== undefined && (
                            <span className="text-xs text-gray-500 ml-2">
                              {skill.years_of_experience} {skill.years_of_experience === 1 ? 'year' : 'years'}
                            </span>
                          )}
                        </div>
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
