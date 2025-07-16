# careerON
*AI-Powered Resume Builder & Job Matching Platform*

## Project Overview

careerON is a comprehensive AI-powered career platform that revolutionizes the job search process by combining intelligent resume building, optimization, and personalized job matching. The platform leverages advanced AI technologies to help job seekers create ATS-compliant resumes, optimize them for specific job descriptions, and discover relevant opportunities through machine learning algorithms.

**🎯 Key Features:**
- 🤖 **AI-Powered Resume Optimization** using NVIDIA LLM API and Google Gemini
- 📄 **Advanced PDF Resume Parsing** with Adobe PDF Services, Doctly, and PyMuPDF
- 🔍 **Intelligent Job Recommendations** using machine learning and semantic similarity
- 📊 **ATS Compatibility Analysis** with detailed scoring and improvement suggestions
- 🎨 **Professional Resume Templates** with high-quality PDF export
- 🔐 **Secure Authentication** with JWT-based user management
- 📱 **Modern React Interface** built with TypeScript and Shadcn/ui components
- 🌐 **LinkedIn Job Scraping** for real-time job discovery

**🏗️ Architecture:**
```
Frontend (React/TypeScript/Vite) ↔ Flask REST API ↔ PostgreSQL Database
                                         ↕
    AI Services: NVIDIA API | Google Gemini | spaCy | SentenceTransformers
                                         ↕
    PDF Processing: Adobe PDF Services | Doctly | PyMuPDF | pdfkit
```

## Table of Contents

- [Tech Stack](#tech-stack)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Configuration](#environment-configuration)
  - [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [API Usage](#api-usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Tech Stack

### Backend (Python/Flask)
- **Python 3.10+** - Core backend language
- **Flask 3.1.1** - Web framework with CORS support
- **SQLAlchemy 2.0.41** - Database ORM with PostgreSQL
- **PyJWT 2.8.0** - JWT authentication
- **Flask-Limiter** - API rate limiting and security
- **Pydantic 2.11.7** - Data validation and serialization

### AI & ML Services
- **NVIDIA API** - LLM-powered text generation and job recommendations
- **Google Gemini** - Advanced AI optimization and content enhancement
- **spaCy** - Natural language processing and entity extraction
- **SentenceTransformers 5.0.0** - Semantic similarity analysis
- **PyTorch 2.7.1** - Machine learning backend

### PDF Processing
- **Adobe PDF Services** - Professional PDF text extraction
- **Doctly** - Alternative PDF parsing service
- **PyMuPDF (fitz)** - PDF document processing
- **pdfkit 1.0.0** - HTML to PDF conversion
- **PyPDF2 3.0.1** - PDF manipulation

### Frontend (React/TypeScript)
- **React 18.3.1** - Modern UI framework
- **TypeScript 5.5.3** - Type-safe JavaScript
- **Vite 5.4.1** - Fast build tool and development server
- **Shadcn/ui** - Beautiful component library
- **Radix UI** - Accessible component primitives
- **TailwindCSS 3.4.11** - Utility-first CSS framework
- **React Hook Form 7.53.0** - Performant form management
- **React Router DOM 6.26.2** - Client-side routing
- **Axios 1.8.4** - HTTP client for API communication
- **Zod 3.23.8** - Runtime type validation

### Web Scraping & Automation
- **Selenium 4.34.0** - Automated job scraping
- **BeautifulSoup4 4.13.4** - HTML parsing
- **WebDriver Manager 4.0.2** - Browser driver management

### Development & Tools
- **ESLint** - JavaScript/TypeScript linting
- **Flake8** - Python code linting
- **MyPy** - Static type checking

## Features

### 🗂️ Resume Management
- **Multiple Resume Support** - Create and manage multiple professional resumes
- **Drag-and-Drop Interface** - Intuitive section reordering and customization
- **Section Visibility Control** - Toggle visibility for specific resume sections
- **Real-time Preview** - Live editing with instant preview capabilities
- **Template Selection** - Choose from professional resume templates

### 📄 Advanced PDF Parsing
- **Multi-Engine Parsing** - Adobe PDF Services, Doctly, and PyMuPDF fallbacks
- **Intelligent Text Extraction** - Advanced NLP heuristics for accurate data parsing
- **Structured Data Extraction** - Automatic extraction of personal info, education, experience, skills, projects
- **Format Support** - Support for various resume formats and layouts
- **OCR Capabilities** - EasyOCR integration for image-based text extraction

### 🧠 AI-Powered Optimization
- **Smart Job Matching** - Paste job descriptions for instant compatibility analysis
- **Semantic Similarity Scoring** - Quantified match scores using sentence transformers
- **Keyword Gap Analysis** - Identification of missing critical keywords
- **AI Content Enhancement** - NVIDIA and Google Gemini powered summary improvements
- **Section-wise Recommendations** - Targeted advice for skills, projects, and experience
- **Resume Boost Generation** - Job-specific content suggestions and paragraphs
- **ATS Compatibility Check** - Detailed analysis with improvement suggestions

### 🎨 Professional Templates & Export
- **Multiple Templates** - Professional resume layouts (default, modern, ATS-optimized)
- **High-Quality PDF Export** - Professional PDF generation with custom styling
- **ATS-Compliant Formatting** - Optimized for Applicant Tracking Systems
- **Print-Ready Layouts** - Publication-quality formatting

### 🔍 Job Discovery & Recommendations
- **LinkedIn Integration** - Automated job scraping from LinkedIn
- **AI-Powered Matching** - NVIDIA LLM-based job recommendations
- **Profile-Based Suggestions** - Personalized recommendations using user resumes
- **Real-time Job Data** - Fresh job listings with location filtering
- **Domain-Specific Matching** - Industry and role-specific recommendations

### 🛡️ Security & Performance
- **JWT Authentication** - Secure token-based authentication
- **Rate Limiting** - API protection with configurable limits
- **CORS Configuration** - Secure cross-origin resource sharing
- **Data Privacy** - Secure user data handling and storage
- **Performance Optimization** - Efficient database queries and caching

## Getting Started

### Prerequisites

Ensure you have the following installed on your system:

- **Python 3.10+** with pip
- **Node.js 18+** and npm
- **PostgreSQL 12+** database server
- **Git** for version control
- **wkhtmltopdf** for PDF generation (Linux: `apt-get install wkhtmltopdf`)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Skullybutcher/careerON.git
cd careerON
```

2. **Set up Python virtual environment:**
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

3. **Install Python dependencies:**
```bash
pip install -r requirements.txt

# Download spaCy English model
python -m spacy download en_core_web_sm
```

4. **Set up frontend dependencies:**
```bash
cd frontend
npm install
cd ..
```

### Environment Configuration

Create a `.env` file in the root directory with the following configuration:

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_super_secret_jwt_key_here

# Database Configuration
SQLALCHEMY_DATABASE_URI=postgresql://username:password@localhost:5432/career_navigator

# AI Service APIs
NVIDIA_API_KEY=your_nvidia_api_key_here
NVIDIA_API_URL=https://integrate.api.nvidia.com/v1/chat/completions
HF_TOKEN=your_huggingface_token_here

# PDF Processing Services
PDF_SERVICES_CLIENT_ID=your_adobe_client_id
PDF_SERVICES_CLIENT_SECRET=your_adobe_client_secret
DOCTLY_API_KEY=your_doctly_api_key

# Performance Settings
DEVICE=cpu  # Set to 'gpu' if CUDA is available

# Optional: Additional Services
SCRAPER_API_KEY=your_scraper_api_key
```

**Required Environment Variables:**
- `SECRET_KEY` - JWT token signing key (generate a strong random string)
- `SQLALCHEMY_DATABASE_URI` - PostgreSQL connection string
- `NVIDIA_API_KEY` - NVIDIA API key for AI features
- `HF_TOKEN` - Hugging Face token for ML models

**Optional but Recommended:**
- `PDF_SERVICES_CLIENT_ID` & `PDF_SERVICES_CLIENT_SECRET` - Adobe PDF Services
- `DOCTLY_API_KEY` - Enhanced PDF parsing

### Database Setup

1. **Create PostgreSQL database:**
```bash
# Using createdb command
createdb career_navigator

# Or using psql
psql -U postgres -c "CREATE DATABASE career_navigator;"
```

2. **Configure database user (if needed):**
```bash
psql -U postgres -c "CREATE USER your_username WITH PASSWORD 'your_password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE career_navigator TO your_username;"
```

3. **Database tables are created automatically** when the application starts for the first time.

## Running the Application

### Development Mode

1. **Start the backend server:**
```bash
# Make sure virtual environment is activated
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Start Flask development server
python app.py

# Alternative method:
flask run
```
Backend will be available at `http://localhost:5000`

2. **Start the frontend development server:**
```bash
cd frontend
npm run dev
```
Frontend will be available at `http://localhost:8080`

### Production Build

```bash
# Build frontend for production
cd frontend
npm run build
cd ..

# The Flask server can serve the built frontend static files
python app.py
```

### API Health Check

Test if the backend is running correctly:
```bash
curl http://localhost:5000/api/users
```

## API Usage

The careerON API provides comprehensive endpoints for resume management, optimization, and job recommendations.

**Base URL:** `http://localhost:5000/api`

### Quick Start Examples

#### Authentication
```bash
# Register a new user
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com", "password": "securepass123"}'

# Login and get JWT token
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "password": "securepass123"}'
```

#### Resume Operations
```bash
# Create a new resume
curl -X POST http://localhost:5000/api/resumes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"title": "Software Engineer Resume", "summary": "Experienced developer..."}'

# Upload and parse a PDF resume
curl -X POST http://localhost:5000/api/resumes/parse \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@resume.pdf"
```

#### AI-Powered Optimization
```bash
# Optimize resume for a specific job
curl -X POST http://localhost:5000/api/resumes/{resume_id}/optimize \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"job_description": "Senior Python Developer with React experience..."}'
```

#### Job Recommendations
```bash
# Get personalized job recommendations
curl -X POST http://localhost:5000/api/recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"user_id": "your_user_id"}'
```

**📚 Complete API Documentation:** See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for comprehensive endpoint reference with all parameters, responses, and examples.

## Project Structure

```
careerON/
├── 📁 api/                    # Flask API layer
│   ├── routes.py             # Main API endpoints and business logic
│   ├── schemas.py            # Pydantic data validation schemas
│   ├── job_recommendation.py # AI-powered job matching service
│   └── limiter.py            # Rate limiting configuration
├── 📁 database/              # Data persistence layer
│   ├── models.py             # SQLAlchemy ORM models
│   └── db.py                 # Database connection and session management
├── 📁 services/              # Core business logic services
│   ├── resume_parser.py      # Multi-engine PDF parsing (Adobe, Doctly, PyMuPDF)
│   ├── resume_generator.py   # HTML/PDF generation and templating
│   ├── resume_optimizer.py   # AI-powered optimization (NVIDIA, Gemini)
│   └── resume_exporter.py    # Export utilities and formatting
├── 📁 frontend/              # React TypeScript frontend
│   ├── src/
│   │   ├── components/       # Reusable UI components (auth, layout, resume, ui)
│   │   ├── pages/           # Main application pages
│   │   ├── contexts/        # React contexts (AuthContext)
│   │   ├── hooks/           # Custom React hooks
│   │   ├── services/        # API service clients
│   │   ├── types/           # TypeScript type definitions
│   │   └── lib/             # Utility functions and configurations
│   ├── public/              # Static assets and icons
│   ├── package.json         # Node.js dependencies and scripts
│   ├── tailwind.config.ts   # TailwindCSS configuration
│   ├── vite.config.ts       # Vite build configuration
│   └── tsconfig.json        # TypeScript configuration
├── 📁 templates/             # Jinja2 HTML resume templates
├── 📁 static/                # CSS/JS static assets for templates
├── 📁 utils/                 # Utility functions and helpers
│   └── linkedin_ws.py        # LinkedIn job scraping automation
├── 📄 app.py                 # Flask application entry point
├── 📄 config.py              # Environment and application configuration
├── 📄 requirements.txt       # Python dependencies with versions
├── 📄 .env                   # Environment variables (create from example)
├── 📄 API_DOCUMENTATION.md   # Comprehensive API documentation
├── 📄 careerON_key_components.md # Technical architecture overview
└── 📄 README.md              # This file
```

## Contributing

We welcome contributions to careerON! Here's how to get involved:

### Development Workflow

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/your-username/careerON.git
   cd careerON
   ```

2. **Create a feature branch:**
   ```bash
   git checkout -b feature/amazing-new-feature
   ```

3. **Set up development environment:**
   ```bash
   # Backend setup
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   
   # Frontend setup
   cd frontend && npm install && cd ..
   ```

4. **Make your changes and test:**
   ```bash
   # Run backend tests
   pytest --cov=. --cov-report=html
   
   # Run frontend linting
   cd frontend && npm run lint && cd ..
   ```

5. **Commit and push:**
   ```bash
   git add .
   git commit -m "feat: add amazing new feature"
   git push origin feature/amazing-new-feature
   ```

6. **Open a Pull Request** with a clear description of your changes.

### Code Standards

- **Python**: Follow PEP 8, use type hints, write docstrings
- **TypeScript**: Use strict mode, proper typing, ESLint compliance
- **Commits**: Use conventional commit messages (`feat:`, `fix:`, `docs:`, etc.)
- **Testing**: Write tests for new features and bug fixes
- **Documentation**: Update docs for API changes and new features

### Development Guidelines

- **Backend**: Add rate limiting to new endpoints, validate input with Pydantic
- **Frontend**: Use Shadcn/ui components, implement proper error handling
- **AI Features**: Include fallback mechanisms for API failures
- **Security**: Never commit API keys or sensitive data

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

**🚀 Built with ❤️ by developers, for job seekers everywhere. Happy career building!**

For questions, bug reports, or feature requests, please [open an issue](https://github.com/Skullybutcher/careerON/issues) on GitHub.
