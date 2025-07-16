# careerON Key Components & Technical Architecture

## Project Overview

careerON is a comprehensive AI-powered career platform that combines intelligent resume building, optimization, and personalized job matching. The system leverages advanced AI technologies including NVIDIA LLM API, Google Gemini, and machine learning models to provide a complete career management solution.

**Tech Stack:** Flask (Backend) + React/TypeScript (Frontend) + PostgreSQL (Database) + AI/ML Services

---

## 1. Backend Services Layer

### 1.1 Resume Parser Service
**Location:** `services/resume_parser.py` | **Class:** `ResumeParser`

**Description:** Advanced multi-engine PDF parsing system that extracts structured data from resume PDFs using three fallback mechanisms for maximum reliability.

**Parsing Engines (Priority Order):**
1. **Doctly API** - Professional PDF parsing service for complex layouts
2. **Adobe PDF Services** - Enterprise-grade text extraction with high accuracy
3. **PyMuPDF (fitz)** - Local fallback parsing for basic PDF processing

**Key Methods:**
- `parse_from_pdf(pdf_file)` - Main parsing entry point with multi-engine fallbacks
- `extract_text_using_adobe_api(pdf_file)` - Adobe PDF Services integration
- `_extract_text_from_pdf(pdf_file)` - PyMuPDF fallback method
- `_identify_sections(text)` - NLP-based section identification
- `_extract_personal_info()`, `_extract_education()`, `_extract_experience()`, `_extract_skills()`, `_extract_projects()` - Section-specific data extraction

**Dependencies:** 
- spaCy (NLP), Adobe PDF Services SDK, Doctly API, PyMuPDF, BeautifulSoup4

**Connected Components:**
- API Route: `/api/resumes/parse`
- Frontend: Resume upload components
- Database: Automatic population of resume sections

### 1.2 Resume Optimizer Service
**Location:** `services/resume_optimizer.py` | **Class:** `ResumeOptimizer`

**Description:** AI-powered resume optimization engine that analyzes job-resume compatibility using multiple AI models and provides intelligent improvement suggestions.

**AI Models Used:**
- **Google Gemini** - Content enhancement and intelligent feedback generation
- **SentenceTransformers ('all-MiniLM-L6-v2')** - Semantic similarity analysis
- **spaCy** - Natural language processing and entity extraction
- **RapidFuzz** - Fast fuzzy string matching for skill comparison

**Key Methods:**
- `optimize_for_job(resume, job_description)` - Main optimization logic with similarity scoring
- `enhance_resume(resume, ats_result, keyword_matches)` - AI-powered improvement suggestions
- `check_ats_compatibility(resume)` - ATS compliance analysis
- `_extract_skills_with_nlp(text)` - NLP-based skill extraction
- `_find_missing_skills(resume_skills, job_skills)` - Gap analysis
- `_generate_suggestions(resume, missing_skills)` - Targeted improvement recommendations

**Features:**
- Semantic similarity scoring (0.0 - 1.0)
- Missing skills identification
- ATS compatibility checking
- AI-generated content improvements
- Job-specific resume boost paragraphs

**Connected Components:**
- API Route: `/api/resumes/{id}/optimize`
- Frontend: Resume optimization pages
- Database: Optimization history and suggestions

### 1.3 Resume Generator Service
**Location:** `services/resume_generator.py` | **Class:** `ResumeGenerator`

**Description:** Professional resume generation service that converts structured resume data into formatted HTML and PDF documents using customizable templates.

**Key Methods:**
- `generate_html(resume_data, template_name)` - Jinja2 template rendering
- `generate_pdf(html_content)` - HTML to PDF conversion using pdfkit
- `_prepare_template_data(resume)` - Data formatting for template compatibility
- `_format_date(date_obj)` - Date formatting utilities

**Template System:**
- Jinja2-based HTML templates in `/templates/` directory
- Professional layouts (default, modern, ATS-optimized)
- Responsive design with print-friendly CSS
- Section visibility controls and custom ordering

**Connected Components:**
- API Route: `/api/resumes/{id}/export-ats`
- Frontend: Resume preview and export features
- Templates: Professional resume layouts

### 1.4 Job Recommendation Engine
**Location:** `api/job_recommendation.py` | **Function:** `llm_recommend_jobs()`

**Description:** AI-powered job recommendation system using NVIDIA LLM API (Gemma model) to analyze user profiles and suggest relevant job titles based on skills, experience, and preferences.

**Key Features:**
- Profile extraction from user resumes
- NVIDIA LLM-powered job title generation
- Skills and experience analysis
- Domain preference consideration
- Integration with job scraping pipeline

**Workflow:**
1. Fetch user resumes and build profile
2. Extract skills, experience, education, certifications
3. Construct AI prompt with user profile
4. Send request to NVIDIA LLM API
5. Parse and return job recommendations

**Connected Components:**
- API Route: `/api/recommend`
- Frontend: Job recommendations page
- Integration: LinkedIn job scraper

### 1.5 LinkedIn Job Scraper
**Location:** `utils/linkedin_ws.py` | **Function:** `scrape_linkedin_jobs()`

**Description:** Automated web scraping system using Selenium to extract job listings from LinkedIn based on keywords, location, and filters.

**Key Features:**
- Headless browser automation with Selenium
- Pagination support for comprehensive results
- Advanced filtering (time, job type, location, experience level)
- Rate limiting and anti-detection mechanisms
- JSON output for structured job data

**Scraping Capabilities:**
- Job title and company extraction
- Location and salary information
- Job description and requirements
- Application links and posting dates
- Skills and qualifications parsing

**Connected Components:**
- API Route: `/api/run-scraper`
- Job recommendation workflow
- Real-time job data updates

---

## 2. API Layer & Routing

### 2.1 Main Routes Handler
**Location:** `api/routes.py` | **Blueprint:** `api`

**Description:** Central Flask blueprint managing all API endpoints with comprehensive CORS support, rate limiting, JWT authentication, and error handling.

**Key Endpoint Categories:**

**Authentication & Users:**
- `POST /login` - JWT authentication with rate limiting (5/min)
- `POST /users` - User registration with email uniqueness validation
- `GET /test` - Health check endpoint

**Resume Management:**
- `POST /resumes` - Create new resume with default section settings
- `GET /resumes/{id}` - Retrieve resume with all sections
- `DELETE /resumes/{id}` - Remove resume and cascade delete sections
- `GET /users/{id}/resumes` - List all user resumes

**Resume Sections (CRUD operations):**
- `GET/PUT /resumes/{id}/sections/personal_info` - Personal information management
- `GET/PUT /resumes/{id}/sections/summary` - Resume summary
- `GET/PUT /resumes/{id}/sections/education` - Education history
- `GET/PUT /resumes/{id}/sections/experience` - Work experience
- `GET/PUT /resumes/{id}/sections/skills` - Skills and competencies
- `GET/PUT /resumes/{id}/sections/projects` - Projects and portfolios

**Resume Services:**
- `POST /resumes/parse` - Multi-engine PDF parsing
- `POST /resumes/{id}/optimize` - AI-powered optimization
- `GET /resumes/{id}/export-ats` - ATS-compliant PDF export

**Job Recommendations:**
- `POST /recommend` - AI-powered job suggestions
- `GET /recommended_jobs.json` - Cached job data
- `POST /run-scraper` - Trigger LinkedIn scraping

### 2.2 Rate Limiting & Security
**Location:** `api/limiter.py` | **Function:** `init_app()`

**Configuration:**
- Global limits: 200 requests/day, 50 requests/hour
- Login endpoint: 5 requests/minute
- In-memory storage for development
- Configurable for Redis in production

### 2.3 Data Validation Schemas
**Location:** `api/schemas.py`

**Description:** Comprehensive Pydantic schemas ensuring data integrity and type safety across all API operations.

**Key Schemas:**
- `UserCreate`, `UserResponse`, `UserLogin` - User authentication data
- `ResumeCreate`, `ResumeResponse` - Resume structure validation
- `PersonalInfoSchema`, `EducationSchema`, `ExperienceSchema` - Section schemas
- `SkillSchema`, `ProjectSchema`, `AchievementSchema` - Additional sections
- `ResumeOptimizeRequest` - Optimization input validation

---

## 3. Database Layer

### 3.1 Database Models
**Location:** `database/models.py`

**Description:** SQLAlchemy ORM models defining the complete data structure with relationships and cascade behaviors.

**Core Models:**

**User Model:**
- Primary key: UUID string
- Fields: name, email (unique), password (hashed), created_at
- Relationships: One-to-many with Resume (cascade delete)

**Resume Model:**
- Primary key: UUID string
- Fields: user_id (FK), title, summary, created_at, updated_at
- JSON field: section_settings (visibility and order configuration)
- Relationships: One-to-one/many with all section models (cascade delete)

**Section Models:**
- `PersonalInfo` - Contact information and social profiles
- `Education` - Institution, degree, GPA, dates
- `Experience` - Company, position, achievements array, dates
- `Skill` - Name, category, proficiency level
- `Project` - Name, description, technologies, links
- `Achievement` - Title, description, date, issuer
- `Certification` - Name, issuer, date, credential ID
- `VolunteerWork` - Organization, role, description
- `Publication` - Title, publisher, date, URL

### 3.2 Database Configuration
**Location:** `database/db.py`

**Features:**
- PostgreSQL connection with SQLAlchemy 2.0+
- Session management with dependency injection
- Connection pooling for performance
- Automatic table creation on startup
- Migration support for schema changes

---

## 4. Frontend Architecture

### 4.1 Application Structure
**Location:** `frontend/src/`

**Framework:** React 18.3.1 with TypeScript 5.5.3
**Build Tool:** Vite 5.4.1 with SWC for fast compilation
**Styling:** TailwindCSS 3.4.11 + Shadcn/ui components

### 4.2 Component Organization

**Core Components (`src/components/`):**
- `auth/` - Login, Register, PrivateRoute components
- `layout/` - Header, Navigation, Layout wrapper
- `resume/` - Resume builder, editor, preview components
- `ui/` - Shadcn/ui component library (Button, Input, Dialog, etc.)

**Page Components (`src/pages/`):**
- `Home.tsx` - Landing page with feature showcase
- `Dashboard.tsx` - User dashboard with resume management
- `auth/Login.tsx`, `auth/Register.tsx` - Authentication pages
- `resume-builder/ResumeBuilder.tsx` - Main resume editing interface
- `resume-optimization/ResumeOptimization.tsx` - AI optimization interface
- `JobRecommendation.tsx` - Job discovery and recommendations

**Context & State Management (`src/contexts/`):**
- `AuthContext.tsx` - Global authentication state management
- JWT token handling and persistence
- User session management

**API Services (`src/services/`):**
- HTTP client configuration with Axios
- API endpoint abstractions
- Error handling and response transformation

### 4.3 Key Frontend Features

**Resume Builder:**
- Drag-and-drop section reordering
- Real-time preview with professional templates
- Section visibility toggles
- Auto-save functionality
- Multi-step form validation

**AI Integration:**
- Job description paste and analysis
- Real-time optimization scoring
- Interactive suggestion implementation
- Progress tracking and feedback

**Job Recommendations:**
- User profile-based matching
- Interactive job search filters
- LinkedIn integration
- Application tracking

---

## 5. AI & Machine Learning Integration

### 5.1 NVIDIA LLM API Integration
**Usage:** Job recommendations, content generation
**Model:** Gemma model family
**Features:** 
- Natural language job title generation
- Profile analysis and matching
- Contextual recommendations

### 5.2 Google Gemini Integration
**Usage:** Resume content enhancement
**Features:**
- Intelligent summary optimization
- Achievement quantification suggestions
- ATS keyword optimization
- Content improvement recommendations

### 5.3 SentenceTransformers
**Model:** `all-MiniLM-L6-v2`
**Usage:** Semantic similarity analysis
**Features:**
- Resume-job description matching
- Skill similarity scoring
- Content relevance analysis

### 5.4 spaCy NLP Pipeline
**Model:** `en_core_web_sm`
**Usage:** Text processing and entity extraction
**Features:**
- Named entity recognition
- Part-of-speech tagging
- Skill and keyword extraction
- Section content parsing

---

## 6. Configuration & Environment

### 6.1 Environment Variables
**Location:** `config.py` + `.env` file

**Required Configuration:**
```bash
# Authentication
SECRET_KEY=jwt_secret_key_here

# Database
SQLALCHEMY_DATABASE_URI=postgresql://user:pass@localhost:5432/career_navigator

# AI Services
NVIDIA_API_KEY=nvidia_api_key
NVIDIA_API_URL=https://integrate.api.nvidia.com/v1/chat/completions
HF_TOKEN=huggingface_token

# PDF Processing
PDF_SERVICES_CLIENT_ID=adobe_client_id
PDF_SERVICES_CLIENT_SECRET=adobe_client_secret
DOCTLY_API_KEY=doctly_api_key

# Performance
DEVICE=cpu  # or gpu for CUDA acceleration
```

### 6.2 Development Dependencies
**Backend:** Flask, SQLAlchemy, Pydantic, spaCy, torch, requests
**Frontend:** React, TypeScript, Vite, TailwindCSS, Axios, React Hook Form
**AI/ML:** sentence-transformers, google-genai, nvidia-api
**PDF:** Adobe PDF Services, PyMuPDF, pdfkit, doctly

---

## 7. Application Flow & User Journey

### 7.1 Resume Creation Flow
1. **User Registration/Login** → JWT token generation
2. **Resume Creation** → Database entry with default sections
3. **PDF Upload (Optional)** → Multi-engine parsing → Section population
4. **Manual Editing** → Section-by-section data entry
5. **Preview & Export** → PDF generation with professional templates

### 7.2 AI Optimization Flow
1. **Job Description Input** → Text analysis and processing
2. **Semantic Analysis** → SentenceTransformers similarity scoring
3. **Skill Gap Analysis** → Missing skills identification
4. **AI Enhancement** → Gemini/NVIDIA content suggestions
5. **Implementation** → User applies suggestions → Updated resume

### 7.3 Job Recommendation Flow
1. **Profile Analysis** → Extract skills, experience, education
2. **LLM Processing** → NVIDIA API job title generation
3. **Job Scraping** → LinkedIn automation for fresh data
4. **Matching Algorithm** → Profile-job compatibility scoring
5. **Recommendation Delivery** → Personalized job suggestions

---

## 8. Security & Performance

### 8.1 Security Measures
- **JWT Authentication** with configurable expiration
- **Rate Limiting** on sensitive endpoints
- **CORS Configuration** for frontend-backend communication
- **Password Hashing** using Werkzeug security
- **Input Validation** with Pydantic schemas
- **SQL Injection Protection** via SQLAlchemy ORM

### 8.2 Performance Optimizations
- **Database Connection Pooling** for concurrent requests
- **Async PDF Processing** with multiple engine fallbacks
- **Efficient AI Model Loading** with caching
- **Frontend Code Splitting** with Vite
- **Image Optimization** and lazy loading
- **API Response Caching** for job recommendations

### 8.3 Error Handling & Monitoring
- **Comprehensive Error Logging** throughout the application
- **Graceful Fallbacks** for AI service failures
- **User-Friendly Error Messages** in frontend
- **API Health Checks** and monitoring endpoints
- **Transaction Rollbacks** for database consistency

---

## 9. Deployment & Infrastructure

### 9.1 Development Environment
- **Backend:** Flask development server with debug mode
- **Frontend:** Vite dev server with hot module replacement
- **Database:** Local PostgreSQL instance
- **Environment:** `.env` file configuration

### 9.2 Production Considerations
- **Backend:** WSGI server (Gunicorn) with multiple workers
- **Frontend:** Static file serving through CDN
- **Database:** Managed PostgreSQL with connection pooling
- **AI Services:** Rate limiting and API key management
- **Monitoring:** Application performance monitoring (APM)
- **Security:** HTTPS, environment variable protection

---

## 10. Future Enhancements & Roadmap

### 10.1 Planned Features
- **Real-time Collaboration** on resume editing
- **Advanced Analytics** for job market insights
- **Mobile Application** for iOS and Android
- **Integration APIs** for third-party career platforms
- **Video Interview Preparation** with AI feedback

### 10.2 Technical Improvements
- **Microservices Architecture** for better scalability
- **GraphQL API** for more efficient data fetching
- **Redis Caching** for improved performance
- **Kubernetes Deployment** for container orchestration
- **Advanced ML Models** for better recommendations

---

**🏗️ Architecture Summary:** careerON combines modern web technologies with cutting-edge AI to deliver a comprehensive career management platform. The modular architecture ensures scalability, maintainability, and extensibility for future enhancements.

**🔗 Integration Points:** All components are designed for loose coupling with well-defined interfaces, enabling independent development and deployment while maintaining system cohesion.