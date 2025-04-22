import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { resumeSectionService } from '../../../services/api';
import { Project } from '../../../types';
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
import { useToast } from '../../../components/ui/use-toast';
import { Plus, Save, Trash, Edit } from 'lucide-react';

const projectSchema = z.object({
  title: z.string().min(1, 'Project title is required'),
  description: z.string().min(1, 'Description is required'),
  technologies: z.array(z.string()).min(1, 'At least one technology is required'),
  start_date: z.string().min(1, 'Start date is required'),
  end_date: z.string().optional(),
  url: z.string().url('Invalid URL format').optional().or(z.literal('')),
});

type ProjectFormValues = z.infer<typeof projectSchema>;

interface ProjectsFormProps {
  resumeId: string | undefined;
}

export function ProjectsForm({ resumeId }: ProjectsFormProps) {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [projects, setProjects] = useState<Project[]>([]);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [isAdding, setIsAdding] = useState(false);
  const [techInput, setTechInput] = useState('');

  const form = useForm<ProjectFormValues>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      title: '',
      description: '',
      technologies: [],
      start_date: '',
      end_date: '',
      url: '',
    },
  });

  useEffect(() => {
    const fetchProjects = async () => {
      if (!resumeId) return;

      try {
        setIsLoading(true);
        const data = await resumeSectionService.getSection(resumeId, 'projects');
        if (Array.isArray(data)) {
          setProjects(data);
        } else {
          setProjects([]);
        }
      } catch (error) {
        console.error('Error fetching projects:', error);
        toast({
          title: 'Error',
          description: 'Failed to fetch projects',
          variant: 'destructive',
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchProjects();
  }, [resumeId]);

  const onSubmit = async (data: ProjectFormValues) => {
    if (!resumeId) return;

    try {
      setIsLoading(true);

      const updatedProjects = [...projects];

      const projectData: Project = {
        title: data.title,
        description: data.description,
        technologies: data.technologies,
        start_date: data.start_date,
        end_date: data.end_date,
        url: data.url,
      };

      if (editingIndex !== null) {
        updatedProjects[editingIndex] = projectData;
      } else {
        updatedProjects.push(projectData);
      }

      await resumeSectionService.updateSection(resumeId, 'projects', updatedProjects);

      setProjects(updatedProjects);
      setEditingIndex(null);
      setIsAdding(false);

      form.reset({
        title: '',
        description: '',
        technologies: [],
        start_date: '',
        end_date: '',
        url: '',
      });

      toast({
        title: 'Project saved',
        description: editingIndex !== null ? 'Project updated successfully' : 'New project added successfully',
      });
    } catch (error) {
      console.error('Error saving project:', error);
      toast({
        title: 'Save failed',
        description: 'There was an error saving your project',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleEdit = (index: number) => {
    const project = projects[index];
    form.reset({
      title: project.title,
      description: project.description,
      technologies: project.technologies,
      start_date: project.start_date,
      end_date: project.end_date || '',
      url: project.url || '',
    });
    setEditingIndex(index);
    setIsAdding(true);
  };

  const handleDelete = async (index: number) => {
    if (!resumeId) return;

    try {
      setIsLoading(true);

      const updatedProjects = [...projects];
      updatedProjects.splice(index, 1);

      await resumeSectionService.updateSection(resumeId, 'projects', updatedProjects);

      setProjects(updatedProjects);

      toast({
        title: 'Project deleted',
        description: 'Project removed successfully',
      });
    } catch (error) {
      console.error('Error deleting project:', error);
      toast({
        title: 'Delete failed',
        description: 'There was an error deleting your project',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddNew = () => {
    form.reset({
      title: '',
      description: '',
      technologies: [],
      start_date: '',
      end_date: '',
      url: '',
    });
    setEditingIndex(null);
    setIsAdding(true);
  };

  const handleCancel = () => {
    setIsAdding(false);
    setEditingIndex(null);
    form.reset();
  };

  const handleAddTech = () => {
    if (techInput.trim()) {
      const currentTechs = form.getValues('technologies') || [];
      form.setValue('technologies', [...currentTechs, techInput.trim()]);
      setTechInput('');
    }
  };

  const handleRemoveTech = (index: number) => {
    const currentTechs = form.getValues('technologies') || [];
    const newTechs = [...currentTechs];
    newTechs.splice(index, 1);
    form.setValue('technologies', newTechs);
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Projects</h2>
        {!isAdding && (
          <Button 
            onClick={handleAddNew}
            className="bg-brand-600 hover:bg-brand-700"
            disabled={isLoading}
          >
            <Plus className="mr-2 h-4 w-4" />
            Add Project
          </Button>
        )}
      </div>
      
      {isAdding ? (
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Project Title</FormLabel>
                  <FormControl>
                    <Input 
                      placeholder="e.g., E-commerce Website, Mobile App, etc." 
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
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Project Description</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Describe what the project does, your role, and key features..."
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
              <FormLabel>Technologies Used</FormLabel>
              
              <div className="flex space-x-2">
                <Input
                  placeholder="Add a technology (e.g., React, Python, etc.)"
                  value={techInput}
                  onChange={(e) => setTechInput(e.target.value)}
                  disabled={isLoading}
                />
                <Button 
                  type="button"
                  onClick={handleAddTech}
                  disabled={isLoading || !techInput.trim()}
                >
                  Add
                </Button>
              </div>
              
              <div className="space-y-2 mt-2">
                {form.watch('technologies')?.map((tech, index) => (
                  <div key={index} className="flex items-center justify-between bg-gray-50 p-2 rounded">
                    <span className="text-sm">{tech}</span>
                    <Button 
                      type="button" 
                      variant="ghost" 
                      size="sm"
                      onClick={() => handleRemoveTech(index)}
                      disabled={isLoading}
                    >
                      <Trash className="h-4 w-4 text-red-500" />
                    </Button>
                  </div>
                ))}
              </div>
              
              {form.formState.errors.technologies && (
                <p className="text-sm font-medium text-destructive">
                  {form.formState.errors.technologies.message}
                </p>
              )}
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                    <FormLabel>End Date (Optional)</FormLabel>
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
                name="url"
                render={({ field }) => (
                  <FormItem className="md:col-span-2">
                    <FormLabel>Project URL (Optional)</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="https://example.com/my-project" 
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
                {isLoading ? 'Saving...' : editingIndex !== null ? 'Update Project' : 'Add Project'}
              </Button>
            </div>
          </form>
        </Form>
      ) : (
        <>
          {projects.length === 0 ? (
            <div className="text-center py-8 border border-dashed rounded-lg">
              <p className="text-gray-500 mb-4">No projects added yet</p>
              <Button 
                onClick={handleAddNew}
                variant="outline"
              >
                <Plus className="mr-2 h-4 w-4" />
                Add Your First Project
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {projects.map((project, index) => (
                <Card key={index}>
                  <CardContent className="p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-medium">{project.title}</h3>
                        <p className="text-sm text-gray-500">
                          {new Date(project.start_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short' })} - 
                          {project.end_date ? new Date(project.end_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short' }) : ' Present'}
                        </p>
                        <p className="mt-2 text-sm">{project.description}</p>
                        
                        <div className="flex flex-wrap gap-1 mt-2">
                          {project.technologies.map((tech, i) => (
                            <span 
                              key={i} 
                              className="text-xs px-2 py-1 bg-brand-100 text-brand-800 rounded-full"
                            >
                              {tech}
                            </span>
                          ))}
                        </div>
                        
                        {project.url && (
                          <a 
                            href={project.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-sm text-brand-600 hover:underline mt-2 inline-block"
                          >
                            View Project
                          </a>
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
