# Key Code Logic Components - careerON Project

## Overview
The careerON project is a comprehensive career management platform that provides resume building, optimization, and job recommendation services. The system is built with a Flask backend, React frontend, and PostgreSQL database.

---

## 1. Backend Services

### 1.1 Resume Parser Service
- **Description:** Extracts structured data from PDF resumes using PyPDF2, spaCy NLP, and OCR techniques. Identifies resume sections and extracts personal info, education, experience, skills, and projects.
- **Location:** `services/resume_parser.py`, class: `ResumeParser`
- **Key Methods:** 
  - `parse_from_pdf()` - Main parsing entry point
  - `_extract_personal_info()`, `_extract_education()`, `_extract_experience()`, `_extract_skills()`, `_extract_projects()`
- **Connected to:** `/api/resumes/parse` route, frontend `ResumeUploader.tsx`

### 1.2 Resume Optimizer Service
- **Description:** Uses machine learning (SentenceTransformers, spaCy) to analyze resume-job fit, identify missing skills, and provide optimization suggestions. Integrates with Google Gemini AI for intelligent feedback.
- **Location:** `services/resume_optimizer.py`, class: `ResumeOptimizer`
- **Key Methods:**
  - `optimize_for_job()` - Main optimization logic with similarity scoring
  - `enhance_resume()` - AI-powered improvement suggestions
  - `check_ats_compatibility()` - ATS compliance checking
- **Connected to:** `/api/resumes/<id>/optimize` route, frontend optimization pages

### 1.3 Resume Generator Service
- **Description:** Converts resume data into formatted HTML/PDF documents using Jinja2 templates and pdfkit. Supports multiple resume templates and section customization.
- **Location:** `services/resume_generator.py`, class: `ResumeGenerator`
- **Key Methods:**
  - `generate_html()` - Template rendering
  - `generate_pdf()` - PDF conversion
  - `_prepare_template_data()` - Data formatting for templates
- **Connected to:** `/api/resumes/<id>/export` route, resume preview/export features

### 1.4 Job Recommendation Engine
- **Description:** Uses NVIDIA LLM API (Gemma model) to analyze user skills, experience, and preferences to recommend relevant job titles. Supports profile-based matching and domain preferences.
- **Location:** `api/job_recommendation.py`, function: `llm_recommend_jobs()`
- **Key Features:**
  - Profile extraction from user resumes
  - LLM-powered job title recommendations
  - Integration with job scraping pipeline
- **Connected to:** `/api/recommend` route, `JobRecommendation.tsx` frontend page

### 1.5 LinkedIn Job Scraper
- **Description:** Web scraping utility using Selenium to extract job listings from LinkedIn based on keywords, location, and filters. Supports headless browsing and pagination.
- **Location:** `utils/linkedin_ws.py`, function: `scrape_linkedin_jobs()`
- **Key Features:**
  - Automated LinkedIn job search
  - Filtering by time, job type, location
  - JSON output for job listings
- **Connected to:** `/api/run-scraper` route, job recommendation workflow

---

## 2. API Layer

### 2.1 Main Routes Handler
- **Description:** Central Flask blueprint managing all API endpoints with CORS support, rate limiting, and authentication. Handles CRUD operations for users, resumes, and resume sections.
- **Location:** `api/routes.py`, blueprint: `api`
- **Key Endpoints:**
  - `/login`, `/users` - Authentication and user management
  - `/resumes` - Resume CRUD operations
  - `/resumes/<id>/sections/*` - Section-specific endpoints
  - `/resumes/<id>/optimize` - Resume optimization
  - `/resumes/<id>/export` - PDF export
  - `/recommend`, `/run-scraper` - Job recommendations

### 2.2 Rate Limiting
- **Description:** Flask-Limiter integration for API rate limiting to prevent abuse and ensure fair usage.
- **Location:** `api/limiter.py`, function: `init_app()`
- **Connected to:** Applied to sensitive endpoints like `/login`

### 2.3 Data Validation Schemas
- **Description:** Pydantic schemas for request/response validation, ensuring data integrity and type safety across all API operations.
- **Location:** `api/schemas.py`
- **Key Schemas:**
  - `UserCreate`, `UserResponse` - User data validation
  - `ResumeCreate`, `ResumeResponse` - Resume structure validation
  - Section schemas for each resume component (Education, Experience, Skills, etc.)
- **Connected to:** All API routes for data validation

---

## 3. Database Models

### 3.1 User and Resume Models
- **Description:** SQLAlchemy ORM models defining the core data structure with relationships between users, resumes, and resume sections.
- **Location:** `database/models.py`
- **Key Models:**
  - `User` - User accounts with authentication
  - `Resume` - Main resume container with section settings
  - Section models: `PersonalInfo`, `Education`, `Experience`, `Skill`, `Project`, `Achievement`, etc.
- **Relationships:** One-to-many between User-Resume, Resume-Sections with cascade deletion

### 3.2 Database Configuration
- **Description:** PostgreSQL database setup with connection pooling, session management, and configuration for production deployment.
- **Location:** `database/db.py`
- **Key Components:**
  - SQLAlchemy engine with connection pooling
  - Session factory with scoped sessions
  - Database dependency injection via `get_db()`
- **Connected to:** All database operations across the application

---

## 4. Frontend Features

### 4.1 Resume Builder Interface
- **Description:** Interactive React components for building and editing resumes with real-time preview, section management, and form validation.
- **Location:** 
  - `frontend/src/pages/resume-builder/ResumeBuilder.tsx`
  - `frontend/src/pages/resume-builder/ResumePreview.tsx`
  - `frontend/src/pages/resume-builder/sections/` directory
- **Key Features:**
  - Drag-and-drop section reordering
  - Real-time preview updates
  - Section visibility controls
  - Form validation and auto-save

### 4.2 Job Recommendation Dashboard
- **Description:** User interface for viewing personalized job recommendations, location-based job search, and job listing management.
- **Location:** `frontend/src/pages/JobRecommendation.tsx`
- **Key Features:**
  - Location-based job search
  - AI-powered job title recommendations
  - Job listing display and filtering
  - Integration with recommendation engine

### 4.3 Resume Management Components
- **Description:** Components for uploading, parsing, and managing multiple resumes with card-based UI and file upload handling.
- **Location:**
  - `frontend/src/components/resume/ResumeUploader.tsx`
  - `frontend/src/components/resume/ResumeCard.tsx`
  - `frontend/src/components/resume/CreateResumeDialog.tsx`
- **Key Features:**
  - PDF upload and parsing
  - Resume template selection
  - Resume metadata management
  - Export functionality

### 4.4 Dashboard and Navigation
- **Description:** Main user dashboard with navigation, authentication state management, and overview of user data.
- **Location:**
  - `frontend/src/pages/Dashboard.tsx`
  - `frontend/src/pages/Home.tsx`
  - `frontend/src/App.tsx`
- **Key Features:**
  - User authentication flow
  - Resume statistics and quick actions
  - Navigation between major features

---

## 5. Configuration and Infrastructure

### 5.1 Application Configuration
- **Description:** Centralized configuration management for database connections, API keys, and environment-specific settings.
- **Location:** `config.py`, class: `Config`
- **Key Settings:**
  - Database URI for PostgreSQL
  - NVIDIA API configuration for LLM
  - Secret keys and security settings
  - Template and static file paths

### 5.2 Main Application Factory
- **Description:** Flask application factory pattern with blueprint registration, CORS setup, database initialization, and rate limiting configuration.
- **Location:** `app.py`, function: `create_app()`
- **Key Features:**
  - Modular blueprint registration
  - Database table creation
  - CORS configuration for frontend integration
  - Development server setup

---

## Integration Flow

The system follows this typical workflow:

1. **User Authentication:** Users register/login via `/api/users` and `/api/login` endpoints
2. **Resume Creation:** Users can either upload PDFs (parsed via `ResumeParser`) or create resumes manually
3. **Resume Building:** Interactive editing through React components with real-time API updates
4. **Job Recommendations:** AI-powered analysis of user profiles to suggest relevant job titles
5. **Job Search:** Automated LinkedIn scraping based on recommendations and user location
6. **Resume Optimization:** AI-driven suggestions to improve resume-job fit using ML models
7. **Export:** Professional PDF generation with customizable templates

This architecture provides a comprehensive career management platform with modern web technologies, AI integration, and robust data management.