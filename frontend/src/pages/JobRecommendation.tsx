
import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Loader2, Briefcase, Plus, X, ExternalLink, MapPin, Building } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';

interface UserProfile {
  skills: string[];
  experience: string;
  education: string;
  certifications: string[];
  preferred_domains: string[];
}

interface JobListing {
  title: string;
  company: string;
  location: string;
  link: string;
  description?: string;
  salary?: string;
}

const JobRecommendation = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  const [profile, setProfile] = useState<UserProfile>({
    skills: [],
    experience: '',
    education: '',
    certifications: [],
    preferred_domains: []
  });
  const [recommendations, setRecommendations] = useState<string[]>([]);
  const [jobListings, setJobListings] = useState<JobListing[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingJobs, setLoadingJobs] = useState(false);
  const [loadingProfile, setLoadingProfile] = useState(true);
  const [hasProfile, setHasProfile] = useState(false);
  const [newSkill, setNewSkill] = useState('');
  const [newDomain, setNewDomain] = useState('');
  const [newCertification, setNewCertification] = useState('');
  const [userLocation, setUserLocation] = useState('United States');

  useEffect(() => {
    fetchUserProfile();
  }, [user]);

  const fetchUserProfile = async () => {
    if (!user) return;

    try {
      const response = await fetch(`http://localhost:5000/api/users/${user.id}/resumes`);
      if (!response.ok) {
        throw new Error('Failed to fetch user resumes');
      }
      const resumes = await response.json();

      if (resumes.length === 0) {
        setProfile({
          skills: [],
          experience: '',
          education: '',
          certifications: [],
          preferred_domains: []
        });
        setHasProfile(false);
      } else {
        // Extract profile data from the first resume or aggregate as needed
        const firstResume = resumes[0];
        setProfile({
          skills: firstResume.skills?.map((s: any) => s.name) || [],
          experience: firstResume.experience?.map((e: any) => e.position).join('; ') || '',
          education: firstResume.education?.map((ed: any) => ed.degree).join('; ') || '',
          certifications: firstResume.certifications?.map((c: any) => c.name) || [],
          preferred_domains: [] // No direct field, can be empty or derived if available
        });
        setHasProfile(true);
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
      toast({
        title: "Error fetching profile",
        description: "Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoadingProfile(false);
    }
  };

  const saveProfile = async () => {
    if (!user) return;

    try {
      const response = await fetch(`http://localhost:5000/api/user/profile`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: user.id,
          skills: profile.skills,
          experience: profile.experience,
          education: profile.education,
          certifications: profile.certifications,
          preferred_domains: profile.preferred_domains
        })
      });

      if (!response.ok) {
        throw new Error('Failed to save profile');
      }

      setHasProfile(true);
      toast({
        title: "Profile saved successfully!",
        description: "Your profile has been updated.",
      });
    } catch (error) {
      console.error('Error saving profile:', error);
      toast({
        title: "Error saving profile",
        description: "Please try again.",
        variant: "destructive",
      });
    }
  };

  const getJobRecommendations = async () => {
    setLoading(true);
    try {
      if (!user) {
        throw new Error('User not authenticated');
      }
      const response = await fetch(`http://localhost:5000/api/recommend`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: user.id })
      });

      if (!response.ok) {
        throw new Error('Failed to get job recommendations');
      }

      const data = await response.json();

      // data.recommendations is expected to be an array of strings
      if (Array.isArray(data.recommendations)) {
        setRecommendations(data.recommendations);
      } else {
        // Fallback: parse string if needed
        let jobTitles: string[] = [];
        try {
          jobTitles = JSON.parse(data.recommendations);
        } catch {
          jobTitles = data.recommendations.split(/\r?\n|,/).map((title: string) => title.trim()).filter(Boolean);
        }
        setRecommendations(jobTitles);
      }
    } catch (error) {
      console.error('Error getting recommendations:', error);
      toast({
        title: "Error getting recommendations",
        description: error.message || "Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const addArrayItem = (field: keyof UserProfile, value: string, setter: (value: string) => void) => {
    if (value.trim()) {
      setProfile(prev => ({
        ...prev,
        [field]: [...(prev[field] as string[]), value.trim()]
      }));
      setter('');
    }
  };

  const removeArrayItem = (field: keyof UserProfile, index: number) => {
    setProfile(prev => ({
      ...prev,
      [field]: (prev[field] as string[]).filter((_, i) => i !== index)
    }));
  };

  const findJobsForTitles = async () => {
    if (!user || recommendations.length === 0) {
      toast({
        title: "No recommendations available",
        description: "Please generate job recommendations first.",
        variant: "destructive",
      });
      return;
    }

    setLoadingJobs(true);
    try {
      // Step 1: Get fresh recommendations from the API
      const recommendResponse = await fetch('http://localhost:5000/api/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: user.id })
      });

      if (!recommendResponse.ok) {
        throw new Error('Failed to fetch fresh recommendations');
      }

      const recommendData = await recommendResponse.json();
      
      // Parse and clean recommendations
      let cleanedTitles: string[] = [];
      if (Array.isArray(recommendData.recommendations)) {
        cleanedTitles = recommendData.recommendations;
      } else {
        try {
          cleanedTitles = JSON.parse(recommendData.recommendations);
        } catch {
          cleanedTitles = recommendData.recommendations
            .split(/\r?\n|,/)
            .map((title: string) => title.trim().replace(/^["']|["']$/g, ''))
            .filter(Boolean);
        }
      }

      // Step 2: Trigger the scraper with the fresh recommendations
      const scrapingUrl = `http://localhost:5000/api/run-scraper`;
      const scraperResponse = await fetch(scrapingUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: user.id, location: userLocation })
      });

      if (!scraperResponse.ok) {
        throw new Error('Failed to scrape job listings');
      }

      // Step 3: Load the generated recommended_jobs.json file
      const jobsResponse = await fetch('http://localhost:5000/api/recommended_jobs.json');
      
      if (!jobsResponse.ok) {
        throw new Error('Failed to load job listings');
      }

      const jobsData = await jobsResponse.json();
      
      // Parse job listings from the response and override location with userLocation
      const parsedJobs: JobListing[] = [];
      
      if (Array.isArray(jobsData)) {
        jobsData.forEach((job: any) => {
          if (job.title && job.company) {
            parsedJobs.push({
              title: job.title,
              company: job.company,
              location: userLocation, // Override with frontend location
              link: job.link || '#',
              description: job.description || '',
              salary: job.salary || ''
            });
          }
        });
      }

      setJobListings(parsedJobs);
      
      toast({
        title: "Jobs found successfully!",
        description: `Found ${parsedJobs.length} job listings for your recommended titles.`,
      });

      // Auto-scroll to job listings
      setTimeout(() => {
        const jobListElement = document.getElementById('job-listings');
        if (jobListElement) {
          jobListElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 100);

    } catch (error) {
      console.error('Error finding jobs:', error);
      toast({
        title: "Error finding jobs",
        description: error instanceof Error ? error.message : "Failed to fetch job listings. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoadingJobs(false);
    }
  };

  if (loadingProfile) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-12 w-12 animate-spin text-brand-600" />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Job Recommendations</h1>
        <p className="text-gray-600">Get personalized job recommendations based on your profile</p>
      </div>

      <div className="grid gap-6">
        {/* Profile Section */}
        <Card>
          <CardHeader>
            <CardTitle>Your Profile</CardTitle>
            <CardDescription>
              {hasProfile ? "Update your profile to get better recommendations" : "Complete your profile to get personalized job recommendations"}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Skills */}
            <div>
              <Label>Skills</Label>
              <div className="flex gap-2 mb-2">
                <Input
                  placeholder="Add a skill"
                  value={newSkill}
                  onChange={(e) => setNewSkill(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addArrayItem('skills', newSkill, setNewSkill)}
                />
                <Button 
                  type="button" 
                  variant="outline"
                  onClick={() => addArrayItem('skills', newSkill, setNewSkill)}
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex flex-wrap gap-2">
                {profile.skills.map((skill, index) => (
                  <Badge key={index} variant="secondary" className="flex items-center gap-1">
                    {skill}
                    <X 
                      className="h-3 w-3 cursor-pointer" 
                      onClick={() => removeArrayItem('skills', index)}
                    />
                  </Badge>
                ))}
              </div>
            </div>

            {/* Experience */}
            <div>
              <Label htmlFor="experience">Experience</Label>
              <Textarea
                id="experience"
                placeholder="Describe your work experience..."
                value={profile.experience}
                onChange={(e) => setProfile(prev => ({ ...prev, experience: e.target.value }))}
              />
            </div>

            {/* Education */}
            <div>
              <Label htmlFor="education">Education</Label>
              <Textarea
                id="education"
                placeholder="Describe your educational background..."
                value={profile.education}
                onChange={(e) => setProfile(prev => ({ ...prev, education: e.target.value }))}
              />
            </div>

            {/* Certifications */}
            <div>
              <Label>Certifications</Label>
              <div className="flex gap-2 mb-2">
                <Input
                  placeholder="Add a certification"
                  value={newCertification}
                  onChange={(e) => setNewCertification(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addArrayItem('certifications', newCertification, setNewCertification)}
                />
                <Button 
                  type="button" 
                  variant="outline"
                  onClick={() => addArrayItem('certifications', newCertification, setNewCertification)}
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex flex-wrap gap-2">
                {profile.certifications.map((cert, index) => (
                  <Badge key={index} variant="secondary" className="flex items-center gap-1">
                    {cert}
                    <X 
                      className="h-3 w-3 cursor-pointer" 
                      onClick={() => removeArrayItem('certifications', index)}
                    />
                  </Badge>
                ))}
              </div>
            </div>

            {/* Preferred Domains */}
            <div>
              <Label>Preferred Domains</Label>
              <div className="flex gap-2 mb-2">
                <Input
                  placeholder="Add a preferred domain"
                  value={newDomain}
                  onChange={(e) => setNewDomain(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addArrayItem('preferred_domains', newDomain, setNewDomain)}
                />
                <Button 
                  type="button" 
                  variant="outline"
                  onClick={() => addArrayItem('preferred_domains', newDomain, setNewDomain)}
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex flex-wrap gap-2">
                {profile.preferred_domains.map((domain, index) => (
                  <Badge key={index} variant="secondary" className="flex items-center gap-1">
                    {domain}
                    <X 
                      className="h-3 w-3 cursor-pointer" 
                      onClick={() => removeArrayItem('preferred_domains', index)}
                    />
                  </Badge>
                ))}
              </div>
            </div>

            <Button onClick={saveProfile} className="w-full">
              Save Profile
            </Button>
          </CardContent>
        </Card>

        {/* Recommendations Section */}
        {hasProfile && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Briefcase className="h-5 w-5" />
                Job Recommendations
              </CardTitle>
              <CardDescription>
                AI-powered job recommendations based on your profile
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button 
                onClick={getJobRecommendations} 
                disabled={loading}
                className="mb-4"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Getting Recommendations...
                  </>
                ) : (
                  'Get Job Recommendations'
                )}
              </Button>

              {recommendations.length > 0 && (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Recommended Jobs for You:</h3>
                  <div className="grid gap-3">
                    {recommendations.map((job, index) => (
                      <div key={index} className="p-4 border rounded-lg bg-gray-50">
                        <h4 className="font-medium text-gray-900">{job}</h4>
                      </div>
                    ))}
                  </div>
                  
                  <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                    <p className="text-blue-900 font-medium mb-2">
                      Want to find jobs for these titles?
                    </p>
                    <p className="text-blue-700 text-sm mb-3">
                      We can help you search for actual job openings matching these recommendations.
                    </p>
                    
                    {/* Location Input - moved here */}
                    <div className="mb-4">
                      <Label htmlFor="location" className="text-blue-900">Job Search Location</Label>
                      <Input
                        id="location"
                        placeholder="Enter your preferred job location"
                        value={userLocation}
                        onChange={(e) => setUserLocation(e.target.value)}
                        className="mt-1"
                      />
                    </div>
                    
                    <Button 
                      variant="outline" 
                      className="border-blue-300 text-blue-700 hover:bg-blue-100"
                      onClick={findJobsForTitles}
                      disabled={loadingJobs}
                    >
                      {loadingJobs ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Finding Jobs...
                        </>
                      ) : (
                        'Find Jobs for These Titles'
                      )}
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Job Listings Section */}
        {jobListings.length > 0 && (
          <Card id="job-listings">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Briefcase className="h-5 w-5" />
                Job Listings
              </CardTitle>
              <CardDescription>
                Actual job openings matching your recommended titles
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {jobListings.map((job, index) => (
                  <div key={index} className="p-4 border rounded-lg hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-semibold text-lg text-gray-900">{job.title}</h4>
                      {job.link && job.link !== '#' && (
                        <a 
                          href={job.link} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 flex items-center gap-1"
                        >
                          <ExternalLink className="h-4 w-4" />
                          View Job
                        </a>
                      )}
                    </div>
                    <div className="flex items-center gap-4 text-gray-600 mb-2">
                      <div className="flex items-center gap-1">
                        <Building className="h-4 w-4" />
                        <span>{job.company}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <MapPin className="h-4 w-4" />
                        <span>{job.location}</span>
                      </div>
                    </div>
                    {job.salary && (
                      <div className="text-green-600 font-medium mb-2">
                        {job.salary}
                      </div>
                    )}
                    {job.description && (
                      <p className="text-gray-700 text-sm line-clamp-3">
                        {job.description}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default JobRecommendation;
