
import axios from 'axios';

// Define base URL for API
const BASE_URL = 'http://localhost:5000/api';

// Create an axios instance
const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to include the token in requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Auth services
export const authService = {
  login: async (email: string, password: string) => {
    const response = await api.post('/login', { email, password });
    localStorage.setItem('token', response.data.token);
    localStorage.setItem('userId', response.data.user.id);
    return response.data;
  },
  register: async (name: string, email: string, password: string) => {
    const response = await api.post('/users', { name, email, password });
    return response.data;
  },
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userId');
  },
  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  },
};

// Resume services
export const resumeService = {
  createResume: async (data: any) => {
    const response = await api.post('/resumes', data);
    return response.data;
  },
  getUserResumes: async (userId: string) => {
    const response = await api.get(`/users/${userId}/resumes`);
    return response.data;
  },
  getResumeDetails: async (resumeId: string) => {
    const response = await api.get(`/resumes/${resumeId}`);
    return response.data;
  },
  updateResume: async (resumeId: string, data: any) => {
    const response = await api.put(`/resumes/${resumeId}`, data);
    return response.data;
  },
  deleteResume: async (resumeId: string) => {
    const response = await api.delete(`/resumes/${resumeId}`);
    return response.data;
  },
  parseResume: async (file: File) => {
    const formData = new FormData();
    formData.append('resume_file', file);
    const response = await api.post('/resumes/parse', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  optimizeResume: async (resumeId: string, jobDescription: string, optimizationLevel: string) => {
    const response = await api.post(`/resumes/${resumeId}/optimize`, {
      job_description: jobDescription,
      optimization_level: optimizationLevel,
    });
    return response.data;
  },
  exportResume: async (resumeId: string, format: string = 'pdf', template: string = 'modern') => {
    const response = await api.get(`/resumes/${resumeId}/export?format=${format}&template=${template}`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

// Resume section services
export const resumeSectionService = {
  getSection: async (resumeId: string, sectionName: string) => {
    const response = await api.get(`/resumes/${resumeId}/sections/${sectionName}`);
    return response.data;
  },
  updateSection: async (resumeId: string, sectionName: string, data: any) => {
    const response = await api.put(`/resumes/${resumeId}/sections/${sectionName}`, data);
    return response.data;
  },
  deleteSection: async (resumeId: string, sectionName: string) => {
    const response = await api.delete(`/resumes/${resumeId}/sections/${sectionName}`);
    return response.data;
  },
};

export default api;
