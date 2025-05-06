
import { Link } from 'react-router-dom';

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-50 border-t border-gray-200 py-8">
      <div className="max-w-7xl mx-auto px-4 md:px-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
              Career Navigator
            </h3>
            <p className="mt-4 text-sm text-gray-600">
              AI-powered resume builder and job matching platform to help you navigate your career journey.
            </p>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
              Features
            </h3>
            <ul className="mt-4 space-y-2">
              <li>
                <Link to="/builder" className="text-sm text-gray-600 hover:text-brand-600">
                  Resume Builder
                </Link>
              </li>
              <li>
                <Link to="/optimization" className="text-sm text-gray-600 hover:text-brand-600">
                  Resume Optimization
                </Link>
              </li>
              <li>
                <Link to="/parsing" className="text-sm text-gray-600 hover:text-brand-600">
                  Resume Parsing
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
              Company
            </h3>
            <ul className="mt-4 space-y-2">
              <li>
                <Link to="/about" className="text-sm text-gray-600 hover:text-brand-600">
                  About Us
                </Link>
              </li>
              <li>
                <Link to="/contact" className="text-sm text-gray-600 hover:text-brand-600">
                  Contact
                </Link>
              </li>
              <li>
                <Link to="/privacy" className="text-sm text-gray-600 hover:text-brand-600">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link to="/terms" className="text-sm text-gray-600 hover:text-brand-600">
                  Terms of Service
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
              Resources
            </h3>
            <ul className="mt-4 space-y-2">
              {/* <li>
                <Link to="/blog" className="text-sm text-gray-600 hover:text-brand-600">
                  Blog
                </Link>
              </li>
              <li>
                <Link to="/guides" className="text-sm text-gray-600 hover:text-brand-600">
                  Career Guides
                </Link>
              </li> */}
              <li>
                <Link to="/faq" className="text-sm text-gray-600 hover:text-brand-600">
                  FAQ
                </Link>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="mt-8 pt-8 border-t border-gray-200">
          <p className="text-center text-sm text-gray-500">
            &copy; {currentYear} Career Opportunities Navigator. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
