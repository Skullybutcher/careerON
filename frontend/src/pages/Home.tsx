
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/AuthContext';
import { 
  FileText, 
  Search, 
  Award, 
  Sparkles, 
  CheckCircle, 
  ChevronRight 
} from 'lucide-react';

export default function Home() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-brand-700 to-brand-900 py-16 md:py-24">
        <div className="container px-4 mx-auto max-w-7xl">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            <div className="text-center md:text-left">
              <h1 className="text-4xl md:text-5xl font-bold text-white leading-tight mb-6">
                AI-Powered Resume Builder & Job Matching Platform
              </h1>
              <p className="text-lg md:text-xl text-white/80 mb-8">
                Create standout resumes, discover perfect job matches, and accelerate your career growth with our intelligent career navigation platform.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center md:justify-start">
                {isAuthenticated ? (
                  <Link to="/dashboard">
                    <Button size="lg" className="w-full sm:w-auto bg-white text-brand-700 hover:bg-gray-100">
                      Go to Dashboard
                      <ChevronRight className="ml-2 h-5 w-5" />
                    </Button>
                  </Link>
                ) : (
                  <>
                    <Link to="/register">
                      <Button size="lg" className="w-full sm:w-auto bg-white text-brand-700 hover:bg-gray-100">
                        Get Started
                        <ChevronRight className="ml-2 h-5 w-5" />
                      </Button>
                    </Link>
                    <Link to="/login">
                      <Button size="lg" variant="outline" className="w-full sm:w-auto border-white text-white hover:bg-white/10">
                        Sign In
                      </Button>
                    </Link>
                  </>
                )}
              </div>
            </div>
            <div className="hidden md:block">
              <img 
                src="https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?auto=format&fit=crop&q=80&w=600" 
                alt="Career Navigator Platform" 
                className="rounded-lg shadow-2xl"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-white">
        <div className="container px-4 mx-auto max-w-7xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Powerful Features to Boost Your Career</h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Our platform combines advanced AI technology with professional career guidance 
              to help you stand out in today's competitive job market.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 flex items-center justify-center rounded-full bg-brand-100 text-brand-600 mb-4">
                <FileText className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold mb-3">AI Resume Builder</h3>
              <p className="text-gray-600">
                Create professionally designed resumes with our AI-powered builder. 
                Tailor your resume for specific roles to maximize your chances.
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 flex items-center justify-center rounded-full bg-brand-100 text-brand-600 mb-4">
                <Search className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Resume Optimization</h3>
              <p className="text-gray-600">
                Analyze your resume against job descriptions to receive personalized 
                suggestions for improvements and keyword optimization.
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 flex items-center justify-center rounded-full bg-brand-100 text-brand-600 mb-4">
                <Award className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Professional Templates</h3>
              <p className="text-gray-600">
                Choose from a variety of professionally designed templates that 
                are tailored for different industries and career stages.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-16 bg-gray-50">
        <div className="container px-4 mx-auto max-w-7xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">How It Works</h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Our simple process helps you create optimized resumes in minutes
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 flex items-center justify-center rounded-full bg-brand-100 text-brand-600 mx-auto mb-4 text-2xl font-bold">
                1
              </div>
              <h3 className="text-xl font-semibold mb-3">Create Resume</h3>
              <p className="text-gray-600">
                Build your resume from scratch or upload an existing one for our AI to analyze.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 flex items-center justify-center rounded-full bg-brand-100 text-brand-600 mx-auto mb-4 text-2xl font-bold">
                2
              </div>
              <h3 className="text-xl font-semibold mb-3">Optimize Content</h3>
              <p className="text-gray-600">
                Get AI-powered suggestions to improve your resume for specific job descriptions.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 flex items-center justify-center rounded-full bg-brand-100 text-brand-600 mx-auto mb-4 text-2xl font-bold">
                3
              </div>
              <h3 className="text-xl font-semibold mb-3">Export & Apply</h3>
              <p className="text-gray-600">
                Download your polished resume in PDF format and start applying with confidence.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-16 bg-white">
        <div className="container px-4 mx-auto max-w-7xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">What Our Users Say</h2>
          </div>
          <h3 className="text-xl font-semibold mb-3 text-center">Nothing yet</h3>
        </div>
        {/* <div className="container px-4 mx-auto max-w-7xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">What Our Users Say</h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Join thousands of professionals who've advanced their careers with our platform
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-lg border border-gray-100 shadow-sm">
              <div className="flex mb-4">
                {[...Array(5)].map((_, i) => (
                  <Sparkles key={i} className="h-5 w-5 text-yellow-400" />
                ))}
              </div>
              <p className="text-gray-700 mb-6">
                "The AI resume builder transformed my job search. I received more interview 
                calls in one week than I did in months with my old resume."
              </p>
              <div className="flex items-center">
                <div className="w-10 h-10 rounded-full bg-gray-200 mr-3"></div>
                <div>
                  <p className="font-semibold">Sarah J.</p>
                  <p className="text-sm text-gray-500">Marketing Specialist</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg border border-gray-100 shadow-sm">
              <div className="flex mb-4">
                {[...Array(5)].map((_, i) => (
                  <Sparkles key={i} className="h-5 w-5 text-yellow-400" />
                ))}
              </div>
              <p className="text-gray-700 mb-6">
                "The resume optimization feature is incredible. It analyzed a job description 
                and suggested exactly what I needed to emphasize in my resume."
              </p>
              <div className="flex items-center">
                <div className="w-10 h-10 rounded-full bg-gray-200 mr-3"></div>
                <div>
                  <p className="font-semibold">Michael T.</p>
                  <p className="text-sm text-gray-500">Software Engineer</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg border border-gray-100 shadow-sm">
              <div className="flex mb-4">
                {[...Array(5)].map((_, i) => (
                  <Sparkles key={i} className="h-5 w-5 text-yellow-400" />
                ))}
              </div>
              <p className="text-gray-700 mb-6">
                "As a recent graduate, I had no idea how to create a professional resume. 
                This platform guided me through the entire process effortlessly."
              </p>
              <div className="flex items-center">
                <div className="w-10 h-10 rounded-full bg-gray-200 mr-3"></div>
                <div>
                  <p className="font-semibold">Emily R.</p>
                  <p className="text-sm text-gray-500">Recent Graduate</p>
                </div>
              </div>
            </div>
          </div>
        </div> */}
      </section>

      {/* CTA Section */}
      <section className="bg-brand-600 py-16">
        <div className="container px-4 mx-auto max-w-7xl">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-white mb-4">
              Ready to Elevate Your Career?
            </h2>
            <p className="text-xl text-white/80 mb-8 max-w-3xl mx-auto">
              Join thousands of professionals who have transformed their career journey with our platform.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {isAuthenticated ? (
                <Link to="/dashboard">
                  <Button size="lg" className="w-full sm:w-auto bg-white text-brand-700 hover:bg-gray-100">
                    Go to Dashboard
                    <ChevronRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
              ) : (
                <>
                  <Link to="/register">
                    <Button size="lg" className="w-full sm:w-auto bg-white text-brand-700 hover:bg-gray-100">
                      Get Started for Free
                      <ChevronRight className="ml-2 h-5 w-5" />
                    </Button>
                  </Link>
                  <Link to="/login">
                    <Button size="lg" variant="outline" className="w-full sm:w-auto border-white text-white hover:bg-white/10">
                      Sign In
                    </Button>
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
