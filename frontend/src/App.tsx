import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from './contexts/AuthContext';
import { Layout } from './components/layout/Layout';
import Home from "./pages/Home";
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import Dashboard from './pages/Dashboard';
import ResumeBuilder from './pages/resume-builder/ResumeBuilder';
import JobRecommendation from './pages/JobRecommendation';
import ResumeOptimization from './pages/resume-optimization/ResumeOptimization';
import NotFound from "./pages/NotFound";
import PrivateRoute from './components/auth/PrivateRoute';

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Layout>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              
              <Route path="/dashboard" element={
                <PrivateRoute>
                  <Dashboard />
                </PrivateRoute>
              } />
              
              <Route path="/job-recommendations" element={
                <PrivateRoute>
                  <JobRecommendation />
                </PrivateRoute>
              } />
              
              <Route path="/builder/:resumeId" element={
                <PrivateRoute>
                  <ResumeBuilder />
                </PrivateRoute>
              } />
              
              <Route path="/optimize/:resumeId" element={
                <PrivateRoute>
                  <ResumeOptimization />
                </PrivateRoute>
              } />
              
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Layout>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
