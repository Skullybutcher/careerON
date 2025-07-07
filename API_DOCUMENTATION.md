# careerON API Documentation

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Configuration](#configuration)
4. [Rate Limiting](#rate-limiting)
5. [API Endpoints](#api-endpoints)
   - [Authentication & Users](#authentication--users)
   - [Resumes](#resumes)
   - [Resume Sections](#resume-sections)
   - [Resume Services](#resume-services)
   - [Job Recommendations](#job-recommendations)
6. [Data Schemas](#data-schemas)
7. [Error Handling](#error-handling)
8. [Usage Examples](#usage-examples)
9. [Setup and Installation](#setup-and-installation)

## Overview

The careerON API is a Flask-based REST API that provides comprehensive resume management, optimization, and job recommendation services. The API enables users to create, manage, and optimize their resumes while receiving personalized job recommendations based on their skills and experience.

**Base URL:** `http://localhost:5000/api`

**Content-Type:** `application/json`

**CORS:** Enabled for `http://localhost:8080`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication with the following configuration:
- **Algorithm:** HS256
- **Token Expiration:** 30 minutes
- **Header Format:** `Authorization: Bearer <token>`

## Configuration

The following environment variables are required:

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT secret key | "dev-secret-key" |
| `SQLALCHEMY_DATABASE_URI` | PostgreSQL connection string | "postgresql://ayush:ayush@localhost:5432/career_navigator" |
| `HF_TOKEN` | Hugging Face API token | - |
| `DEVICE` | Processing device (cpu/gpu) | "cpu" |
| `NVIDIA_API_URL` | NVIDIA API endpoint | "https://integrate.api.nvidia.com/v1/chat/completions" |
| `NVIDIA_API_KEY` | NVIDIA API key | Required for job recommendations |

## Rate Limiting

The API implements rate limiting with the following defaults:
- **Global Limits:** 200 requests per day, 50 requests per hour
- **Login Endpoint:** 5 requests per minute
- **Storage:** In-memory (development)

## API Endpoints

### Authentication & Users

#### POST /login
Authenticate user and receive JWT token.

**Rate Limit:** 5 per minute

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user-uuid",
    "name": "John Doe",
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

**Error Responses:**
- `400` - Invalid input data
- `401` - Invalid credentials

#### POST /users
Create a new user account.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (201):**
```json
{
  "id": "user-uuid",
  "name": "John Doe",
  "email": "user@example.com",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Error Responses:**
- `400` - Invalid user data
- `409` - User with email already exists

#### GET /test
Health check endpoint.

**Response (200):**
```json
{
  "message": "API is working"
}
```

### Resumes

#### POST /resumes
Create a new resume.

**Request Body:**
```json
{
  "user_id": "user-uuid",
  "title": "Software Engineer Resume",
  "summary": "Experienced software engineer with 5+ years of experience...",
  "section_settings": [
    {
      "name": "personal_info",
      "visible": true,
      "order": 1
    },
    {
      "name": "summary", 
      "visible": true,
      "order": 2
    }
  ]
}
```

**Response (201):**
```json
{
  "id": "resume-uuid",
  "user_id": "user-uuid",
  "title": "Software Engineer Resume",
  "summary": "Experienced software engineer...",
  "section_settings": [...],
  "personal_info": null,
  "education": [],
  "experience": [],
  "skills": [],
  "projects": [],
  "achievements": [],
  "extracurriculars": [],
  "courses": [],
  "certifications": [],
  "volunteer_work": [],
  "publications": [],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /resumes/{resume_id}
Retrieve a specific resume by ID.

**Response (200):**
```json
{
  "id": "resume-uuid",
  "user_id": "user-uuid",
  "title": "Software Engineer Resume",
  "summary": "Experienced software engineer...",
  "section_settings": [...],
  "personal_info": {...},
  "education": [...],
  "experience": [...],
  "skills": [...],
  "projects": [...],
  "achievements": [...],
  "extracurriculars": [...],
  "courses": [...],
  "certifications": [...],
  "volunteer_work": [...],
  "publications": [...],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Error Responses:**
- `404` - Resume not found

#### DELETE /resumes/{resume_id}
Delete a specific resume.

**Response (200):**
```json
{
  "message": "Resume deleted successfully"
}
```

#### GET /users/{user_id}/resumes
Get all resumes for a specific user.

**Response (200):**
```json
[
  {
    "id": "resume-uuid-1",
    "user_id": "user-uuid",
    "title": "Software Engineer Resume",
    "summary": "...",
    "section_settings": [...],
    "personal_info": {...},
    "education": [...],
    "experience": [...],
    "skills": [...],
    "projects": [...],
    "achievements": [...],
    "extracurriculars": [...],
    "courses": [...],
    "certifications": [...],
    "volunteer_work": [...],
    "publications": [...],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

#### POST /resumes/{resume_id}/optimize
Optimize resume for a specific job description.

**Request Body:**
```json
{
  "job_description": "We are looking for a Senior Software Engineer with experience in Python, React, and cloud technologies..."
}
```

**Response (200):**
```json
{
  "optimization": {
    "score": 0.85,
    "suggestions": [
      "Add more Python-specific achievements",
      "Highlight cloud technology experience"
    ],
    "missing_skills": ["AWS", "Docker"],
    "keyword_matches": {
      "python": 0.9,
      "react": 0.8,
      "cloud": 0.6
    }
  },
  "improvement_advice": {
    "enhanced_summary": "Updated summary with better keyword optimization...",
    "skill_recommendations": ["Consider adding AWS certification"],
    "experience_enhancements": ["Quantify your Python development impact"]
  }
}
```

#### GET /resumes/{resume_id}/export
Export resume as PDF.

**Query Parameters:**
- `format` (optional): Export format, default "pdf"
- `template` (optional): Template style ("default" or "modern"), default "default"

**Response (200):**
- **Content-Type:** `application/pdf`
- **Content-Disposition:** `attachment; filename=resume_{resume_id}.pdf`

**Error Responses:**
- `400` - Unsupported export format
- `404` - Resume not found

### Resume Sections

#### GET/PUT /resumes/{resume_id}/sections/personal_info
Manage personal information section.

**PUT Request Body:**
```json
{
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1-555-123-4567",
  "location": "San Francisco, CA",
  "linkedin": "https://linkedin.com/in/johndoe",
  "github": "https://github.com/johndoe",
  "portfolio": "https://johndoe.dev"
}
```

#### GET/PUT /resumes/{resume_id}/sections/summary
Manage resume summary section.

**PUT Request Body:**
```json
{
  "summary": "Experienced software engineer with 5+ years of experience in full-stack development..."
}
```

#### GET/PUT /resumes/{resume_id}/sections/education
Manage education section.

**PUT Request Body:**
```json
[
  {
    "institution": "University of California, Berkeley",
    "degree": "Bachelor of Science",
    "field_of_study": "Computer Science",
    "start_date": "2018-08-01",
    "end_date": "2022-05-01",
    "gpa": 3.8,
    "description": "Relevant coursework: Data Structures, Algorithms, Software Engineering"
  }
]
```

#### GET/PUT /resumes/{resume_id}/sections/experience
Manage work experience section.

**PUT Request Body:**
```json
[
  {
    "company": "Tech Corp",
    "position": "Senior Software Engineer",
    "location": "San Francisco, CA",
    "start_date": "2022-06-01",
    "end_date": null,
    "current": true,
    "description": "Lead development of microservices architecture...",
    "achievements": [
      "Reduced API response time by 40%",
      "Led team of 5 engineers"
    ]
  }
]
```

#### GET/PUT /resumes/{resume_id}/sections/skills
Manage skills section.

**PUT Request Body:**
```json
[
  {
    "name": "Python",
    "level": "Expert",
    "category": "Programming Languages"
  },
  {
    "name": "React",
    "level": "Advanced",
    "category": "Frontend Frameworks"
  }
]
```

#### GET/PUT /resumes/{resume_id}/sections/projects
Manage projects section.

**PUT Request Body:**
```json
[
  {
    "title": "E-commerce Platform",
    "description": "Built a full-stack e-commerce platform using React and Node.js",
    "technologies": ["React", "Node.js", "MongoDB", "AWS"],
    "start_date": "2023-01-01",
    "end_date": "2023-06-01",
    "link": "https://github.com/johndoe/ecommerce"
  }
]
```

### Resume Services

#### POST /resumes/parse
Parse resume data from uploaded PDF file.

**Request:**
- **Content-Type:** `multipart/form-data`
- **Form Field:** `resume_file` (PDF file)

**Response (200):**
```json
{
  "personal_info": {
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-123-4567"
  },
  "education": [...],
  "experience": [...],
  "skills": [...],
  "summary": "Extracted summary from PDF..."
}
```

**Error Responses:**
- `400` - No file uploaded or empty filename
- `500` - PDF parsing error

### Job Recommendations

#### POST /recommend
Get personalized job recommendations based on user profile.

**Request Body:**
```json
{
  "user_id": "user-uuid"
}
```

**Response (200):**
```json
{
  "recommendations": [
    "Senior Software Engineer",
    "Full Stack Developer",
    "Backend Engineer",
    "DevOps Engineer",
    "Technical Lead"
  ]
}
```

**Error Responses:**
- `400` - Missing user_id
- `500` - Missing NVIDIA_API_KEY
- `502` - Failed to fetch user resumes or LLM API call failed

#### GET /recommended_jobs.json
Get cached job recommendations from file.

**Response (200):**
```json
[
  {
    "title": "Senior Software Engineer",
    "company": "Tech Corp",
    "location": "San Francisco, CA",
    "salary": 150000,
    "description": "We are looking for a senior software engineer...",
    "url": "https://example.com/job/123"
  }
]
```

#### POST /run-scraper
Run job scraper to fetch latest job postings.

**Request Body:**
```json
{
  "user_id": "user-uuid",
  "location": "San Francisco, CA"
}
```

**Response (200):**
```json
{
  "recommended_jobs": [
    {
      "title": "Senior Software Engineer",
      "company": "Tech Corp",
      "location": "San Francisco, CA",
      "description": "...",
      "url": "..."
    }
  ]
}
```

## Data Schemas

### User Schemas

#### UserCreate
```json
{
  "name": "string (required)",
  "email": "email (required)",
  "password": "string (required)"
}
```

#### UserResponse
```json
{
  "id": "string",
  "name": "string",
  "email": "string",
  "created_at": "datetime"
}
```

#### UserLogin
```json
{
  "email": "email (required)",
  "password": "string (required)"
}
```

### Resume Schemas

#### PersonalInfoSchema
```json
{
  "full_name": "string (required)",
  "email": "email (required)",
  "phone": "string (optional)",
  "location": "string (optional)",
  "linkedin": "string (optional)",
  "github": "string (optional)",
  "portfolio": "string (optional)"
}
```

#### EducationSchema
```json
{
  "institution": "string (required)",
  "degree": "string (required)",
  "field_of_study": "string (optional)",
  "start_date": "date (optional)",
  "end_date": "date (optional)",
  "gpa": "float (optional)",
  "description": "string (optional)"
}
```

#### ExperienceSchema
```json
{
  "company": "string (required)",
  "position": "string (required)",
  "location": "string (optional)",
  "start_date": "date (optional)",
  "end_date": "date (optional)",
  "current": "boolean (default: false)",
  "description": "string (optional)",
  "achievements": "array of strings (optional)"
}
```

#### SkillSchema
```json
{
  "name": "string (required)",
  "level": "string (optional)",
  "category": "string (optional)"
}
```

#### ProjectSchema
```json
{
  "title": "string (required)",
  "description": "string (optional)",
  "technologies": "array of strings (optional)",
  "start_date": "date (optional)",
  "end_date": "date (optional)",
  "link": "string (optional)"
}
```

#### AchievementSchema
```json
{
  "title": "string (required)",
  "description": "string (optional)",
  "date": "date (optional)",
  "issuer": "string (optional)"
}
```

#### CertificationSchema
```json
{
  "name": "string (required)",
  "issuer": "string (optional)",
  "date": "date (optional)",
  "credential_id": "string (optional)",
  "url": "string (optional)"
}
```

## Error Handling

The API returns standard HTTP status codes with JSON error responses:

```json
{
  "error": "Error description"
}
```

**Common Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `409` - Conflict
- `500` - Internal Server Error
- `502` - Bad Gateway

## Usage Examples

### Starting the Server
```bash
python app.py
```

The server will start on `http://localhost:5000` with debug mode enabled.

### cURL Examples

#### Create User
```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123"
  }'
```

#### Login
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'
```

#### Create Resume
```bash
curl -X POST http://localhost:5000/api/resumes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "user_id": "user-uuid",
    "title": "My Resume",
    "summary": "Experienced professional..."
  }'
```

#### Get Job Recommendations
```bash
curl -X POST http://localhost:5000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-uuid"
  }'
```

### Postman Collection

You can import the following into Postman for easy testing:

1. Set base URL: `http://localhost:5000/api`
2. Add environment variables:
   - `base_url`: `http://localhost:5000/api`
   - `jwt_token`: `<your-jwt-token-after-login>`
3. Use `{{base_url}}` and `{{jwt_token}}` in your requests

## Setup and Installation

### Prerequisites
- Python 3.8+
- PostgreSQL database
- Optional: NVIDIA API key for job recommendations

### Installation Steps

1. **Clone the repository:**
```bash
git clone <repository-url>
cd careerON
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Configure database:**
```bash
# Update SQLALCHEMY_DATABASE_URI in config.py
# Create PostgreSQL database: career_navigator
```

5. **Run database migrations:**
```bash
python -c "from app import create_app; from database.db import Base, engine; Base.metadata.create_all(bind=engine)"
```

6. **Start the application:**
```bash
python app.py
```

The API will be available at `http://localhost:5000`.

### Dependencies

Key dependencies from `requirements.txt`:
- Flask - Web framework
- SQLAlchemy - ORM
- Pydantic - Data validation
- Flask-CORS - Cross-origin requests
- Flask-Limiter - Rate limiting
- PyJWT - JWT token handling
- requests - HTTP client
- pdfkit - PDF generation

For complete list, see `requirements.txt`.
