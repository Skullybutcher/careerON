# careerON API Documentation

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base Configuration](#base-configuration)
4. [Rate Limiting](#rate-limiting)
5. [API Endpoints](#api-endpoints)
   - [Authentication & Users](#authentication--users)
   - [Resume Management](#resume-management)
   - [Resume Sections](#resume-sections)
   - [Resume Services](#resume-services)
   - [Job Recommendations](#job-recommendations)
   - [Utility Endpoints](#utility-endpoints)
6. [Data Schemas](#data-schemas)
7. [Error Handling](#error-handling)
8. [Usage Examples](#usage-examples)

## Overview

The careerON API is a comprehensive Flask-based REST API that powers an AI-driven career platform. It provides resume management, intelligent PDF parsing, AI-powered optimization, and personalized job recommendations through advanced machine learning models.

**Base URL:** `http://localhost:5000/api`

**Content-Type:** `application/json`

**CORS:** Enabled for `http://localhost:8080` with support for credentials

**Features:**
- 🔐 JWT-based authentication
- 📄 Multi-engine PDF parsing (Adobe, Doctly, PyMuPDF)
- 🤖 AI-powered resume optimization (NVIDIA LLM, Google Gemini)
- 🎯 Intelligent job recommendations
- 📊 ATS compatibility analysis
- 🎨 Professional PDF export
- 🔒 Rate limiting and security

## Authentication

The API uses JWT (JSON Web Tokens) for secure authentication:

- **Algorithm:** HS256
- **Token Expiration:** 30 minutes
- **Header Format:** `Authorization: Bearer <token>`
- **Required for:** All endpoints except `/login`, `/users` (registration), and `/test`

## Base Configuration

**Environment Variables:**

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | JWT secret key | ✅ |
| `SQLALCHEMY_DATABASE_URI` | PostgreSQL connection string | ✅ |
| `NVIDIA_API_KEY` | NVIDIA API for AI features | ✅ |
| `NVIDIA_API_URL` | NVIDIA API endpoint | ✅ |
| `HF_TOKEN` | Hugging Face token | ✅ |
| `PDF_SERVICES_CLIENT_ID` | Adobe PDF Services ID | ⚠️ |
| `PDF_SERVICES_CLIENT_SECRET` | Adobe PDF Services secret | ⚠️ |
| `DOCTLY_API_KEY` | Doctly PDF parsing API | ⚠️ |
| `DEVICE` | Processing device (cpu/gpu) | ⚠️ |

## Rate Limiting

The API implements rate limiting for security:

- **Global Limits:** 200 requests per day, 50 requests per hour
- **Login Endpoint:** 5 requests per minute
- **Storage:** In-memory (configurable)
- **Headers:** Rate limit info included in response headers

## API Endpoints

### Authentication & Users

#### POST /login
Authenticate user and receive JWT access token.

**Rate Limit:** 5 per minute

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "user-uuid-here",
    "name": "John Doe",
    "email": "user@example.com",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

**Error Responses:**
- `400` - Invalid request data
- `401` - Invalid credentials
- `429` - Rate limit exceeded

#### POST /users
Register a new user account.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "password": "securePassword123"
}
```

**Response (201):**
```json
{
  "id": "user-uuid-here",
  "name": "John Doe",
  "email": "john.doe@example.com",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**
- `400` - Invalid user data
- `409` - User already exists

#### GET /test
Health check endpoint (no authentication required).

**Response (200):**
```json
{
  "message": "API is working!",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Resume Management

#### POST /resumes
Create a new resume for a user.

**Authentication:** Required

**Request Body:**
```json
{
  "user_id": "user-uuid-here",
  "title": "Software Engineer Resume",
  "summary": "Experienced software engineer with 5+ years in Python and React development...",
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
  "id": "resume-uuid-here",
  "user_id": "user-uuid-here",
  "title": "Software Engineer Resume",
  "summary": "Experienced software engineer...",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "section_settings": [...]
}
```

#### GET /resumes/{resume_id}
Retrieve a specific resume with all its sections.

**Authentication:** Required

**Response (200):**
```json
{
  "id": "resume-uuid-here",
  "user_id": "user-uuid-here",
  "title": "Software Engineer Resume",
  "summary": "Experienced software engineer...",
  "personal_info": {
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-555-0123",
    "location": "San Francisco, CA",
    "linkedin": "https://linkedin.com/in/johndoe",
    "github": "https://github.com/johndoe",
    "portfolio": "https://johndoe.dev"
  },
  "education": [...],
  "experience": [...],
  "skills": [...],
  "projects": [...],
  "section_settings": [...]
}
```

#### DELETE /resumes/{resume_id}
Delete a specific resume and all its sections.

**Authentication:** Required

**Response (200):**
```json
{
  "message": "Resume deleted successfully"
}
```

#### GET /users/{user_id}/resumes
Get all resumes for a specific user.

**Authentication:** Required

**Response (200):**
```json
[
  {
    "id": "resume-uuid-1",
    "title": "Software Engineer Resume",
    "summary": "Experienced developer...",
    "created_at": "2024-01-15T10:30:00Z",
    "personal_info": {...}
  },
  {
    "id": "resume-uuid-2",
    "title": "Data Scientist Resume",
    "summary": "ML specialist with...",
    "created_at": "2024-01-16T14:20:00Z",
    "personal_info": {...}
  }
]
```

### Resume Sections

All section endpoints follow the pattern: `/resumes/{resume_id}/sections/{section_name}`

#### GET/PUT /resumes/{resume_id}/sections/personal_info
Manage personal information section.

**PUT Request Body:**
```json
{
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1-555-0123",
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
  "summary": "Experienced software engineer with 5+ years of expertise in full-stack development..."
}
```

#### GET/PUT /resumes/{resume_id}/sections/education
Manage education section.

**PUT Request Body:**
```json
{
  "education": [
    {
      "institution": "Stanford University",
      "degree": "Bachelor of Science",
      "field_of_study": "Computer Science",
      "start_date": "2018-09-01",
      "end_date": "2022-06-15",
      "gpa": 3.8,
      "description": "Relevant coursework: Data Structures, Algorithms, Machine Learning"
    }
  ]
}
```

#### GET/PUT /resumes/{resume_id}/sections/experience
Manage work experience section.

**PUT Request Body:**
```json
{
  "experience": [
    {
      "company": "Tech Innovations Inc.",
      "position": "Senior Software Engineer",
      "location": "San Francisco, CA",
      "start_date": "2022-07-01",
      "end_date": null,
      "current": true,
      "description": "Lead development of microservices architecture...",
      "achievements": [
        "Improved system performance by 40%",
        "Led team of 5 developers",
        "Implemented CI/CD pipeline"
      ]
    }
  ]
}
```

#### GET/PUT /resumes/{resume_id}/sections/skills
Manage skills section.

**PUT Request Body:**
```json
{
  "skills": [
    {
      "name": "Python",
      "category": "Programming Languages",
      "proficiency": "Expert"
    },
    {
      "name": "React",
      "category": "Frontend Frameworks",
      "proficiency": "Advanced"
    }
  ]
}
```

#### GET/PUT /resumes/{resume_id}/sections/projects
Manage projects section.

**PUT Request Body:**
```json
{
  "projects": [
    {
      "name": "AI Resume Optimizer",
      "description": "Machine learning application that optimizes resumes for ATS systems...",
      "technologies": ["Python", "TensorFlow", "Flask", "React"],
      "link": "https://github.com/johndoe/resume-optimizer",
      "start_date": "2023-01-01",
      "end_date": "2023-06-30"
    }
  ]
}
```

### Resume Services

#### POST /resumes/parse
Upload and parse a PDF resume to extract structured data.

**Authentication:** Required

**Request:** Multipart form data
- `file`: PDF file (required)

**Response (200):**
```json
{
  "personal_info": {
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-555-0123"
  },
  "summary": "Experienced software engineer...",
  "education": [...],
  "experience": [...],
  "skills": [...],
  "projects": [...]
}
```

**Parsing Methods (in order of priority):**
1. **Doctly API** - Professional PDF parsing service
2. **Adobe PDF Services** - Enterprise-grade text extraction
3. **PyMuPDF** - Fallback local parsing

#### POST /resumes/{resume_id}/optimize
Optimize resume content for a specific job description using AI.

**Authentication:** Required

**Request Body:**
```json
{
  "job_description": "We are seeking a Senior Python Developer with experience in Django, React, and AWS. The ideal candidate will have 5+ years of experience in building scalable web applications..."
}
```

**Response (200):**
```json
{
  "score": 0.78,
  "feedback": "Good match with room for improvement",
  "suggestions": {
    "skills": [
      "Add AWS experience to your skills section",
      "Highlight Django projects more prominently"
    ],
    "experience": [
      "Quantify your impact with specific metrics",
      "Emphasize scalability achievements"
    ]
  },
  "optimized_summary": "Results-driven Senior Python Developer with 5+ years of experience building scalable web applications using Django and React...",
  "missing_skills": ["AWS", "Django", "Microservices"],
  "resume_boost_paragraph": "To better align with this Senior Python Developer position, consider highlighting your experience with cloud technologies like AWS..."
}
```

**AI Models Used:**
- **NVIDIA LLM API** - Advanced text generation and analysis
- **Google Gemini** - Content enhancement and suggestions
- **SentenceTransformers** - Semantic similarity scoring
- **spaCy** - Natural language processing

#### GET /resumes/{resume_id}/export-ats
Export resume as ATS-compliant PDF.

**Authentication:** Required

**Query Parameters:**
- `format`: Export format (default: "pdf")

**Response:** PDF file stream

**Headers:**
- `Content-Type`: application/pdf
- `Content-Disposition`: attachment; filename="resume.pdf"

### Job Recommendations

#### POST /recommend
Get personalized job recommendations based on user profile.

**Authentication:** Required

**Request Body:**
```json
{
  "user_id": "user-uuid-here",
  "preferences": {
    "location": "San Francisco, CA",
    "job_type": "full-time",
    "remote": true,
    "salary_min": 100000
  }
}
```

**Response (200):**
```json
{
  "recommendations": [
    "Senior Python Developer",
    "Full Stack Engineer",
    "Backend Software Engineer",
    "DevOps Engineer",
    "Machine Learning Engineer"
  ],
  "match_scores": [0.92, 0.88, 0.85, 0.82, 0.79],
  "generated_at": "2024-01-15T10:30:00Z"
}
```

#### GET /recommended_jobs.json
Get cached job recommendations data.

**Authentication:** Required

**Response (200):** Array of job listings with details

#### POST /run-scraper
Trigger LinkedIn job scraping for fresh job data.

**Authentication:** Required

**Request Body:**
```json
{
  "keywords": ["python developer", "software engineer"],
  "location": "San Francisco",
  "job_type": "full-time",
  "max_results": 50
}
```

**Response (200):**
```json
{
  "status": "started",
  "job_id": "scraper-task-uuid",
  "estimated_time": "2-5 minutes"
}
```

### Utility Endpoints

#### OPTIONS /recommend
CORS preflight request for job recommendations.

#### OPTIONS /resumes/{resume_id}/optimize
CORS preflight request for resume optimization.

#### OPTIONS /resumes/{resume_id}/export-ats
CORS preflight request for resume export.

## Data Schemas

### User Schema
```typescript
interface User {
  id: string;
  name: string;
  email: string;
  created_at: string;
}

interface UserCreate {
  name: string;
  email: string;
  password: string;
}
```

### Resume Schema
```typescript
interface Resume {
  id: string;
  user_id: string;
  title: string;
  summary: string;
  created_at: string;
  updated_at: string;
  section_settings: SectionSetting[];
  personal_info?: PersonalInfo;
  education?: Education[];
  experience?: Experience[];
  skills?: Skill[];
  projects?: Project[];
  achievements?: Achievement[];
  certifications?: Certification[];
  // ... other sections
}

interface SectionSetting {
  name: string;
  visible: boolean;
  order: number;
}
```

### Section Schemas
```typescript
interface PersonalInfo {
  full_name: string;
  email: string;
  phone?: string;
  location?: string;
  linkedin?: string;
  github?: string;
  portfolio?: string;
}

interface Experience {
  company: string;
  position: string;
  location?: string;
  start_date?: string;
  end_date?: string;
  current: boolean;
  description?: string;
  achievements?: string[];
}

interface Education {
  institution: string;
  degree: string;
  field_of_study?: string;
  start_date?: string;
  end_date?: string;
  gpa?: number;
  description?: string;
}

interface Skill {
  name: string;
  category?: string;
  proficiency?: string;
}

interface Project {
  name: string;
  description?: string;
  technologies?: string[];
  link?: string;
  start_date?: string;
  end_date?: string;
}
```

## Error Handling

### Standard Error Response Format
```json
{
  "error": "Descriptive error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "specific field error"
  }
}
```

### HTTP Status Codes

| Code | Description | Usage |
|------|-------------|-------|
| 200 | OK | Successful GET/PUT requests |
| 201 | Created | Successful POST requests |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side errors |
| 502 | Bad Gateway | External service errors |

### Common Error Scenarios

**Authentication Errors:**
```json
{
  "error": "Authentication required",
  "code": "AUTH_REQUIRED"
}
```

**Validation Errors:**
```json
{
  "error": "Invalid user data: email is required",
  "code": "VALIDATION_ERROR",
  "details": {
    "email": "This field is required"
  }
}
```

**Rate Limiting:**
```json
{
  "error": "Rate limit exceeded",
  "code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60
}
```

## Usage Examples

### Complete Workflow Example

1. **Register a new user:**
```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Developer",
    "email": "jane@example.com",
    "password": "securePass123"
  }'
```

2. **Login to get access token:**
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane@example.com",
    "password": "securePass123"
  }'
# Save the access_token from response
```

3. **Create a new resume:**
```bash
curl -X POST http://localhost:5000/api/resumes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "user_id": "user-uuid-from-login",
    "title": "Senior Developer Resume",
    "summary": "Experienced full-stack developer..."
  }'
```

4. **Upload and parse existing resume:**
```bash
curl -X POST http://localhost:5000/api/resumes/parse \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@existing_resume.pdf"
```

5. **Add personal information:**
```bash
curl -X PUT http://localhost:5000/api/resumes/RESUME_ID/sections/personal_info \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "full_name": "Jane Developer",
    "email": "jane@example.com",
    "phone": "+1-555-0123",
    "location": "Seattle, WA",
    "linkedin": "https://linkedin.com/in/janedeveloper"
  }'
```

6. **Optimize resume for a job:**
```bash
curl -X POST http://localhost:5000/api/resumes/RESUME_ID/optimize \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "job_description": "We are seeking a Senior Full Stack Developer with expertise in React, Python, and AWS..."
  }'
```

7. **Get job recommendations:**
```bash
curl -X POST http://localhost:5000/api/recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "user_id": "user-uuid-here"
  }'
```

8. **Export optimized resume:**
```bash
curl -X GET http://localhost:5000/api/resumes/RESUME_ID/export-ats?format=pdf \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  --output optimized_resume.pdf
```

### JavaScript/TypeScript Examples

```typescript
// API Client setup
const API_BASE = 'http://localhost:5000/api';
const token = localStorage.getItem('access_token');

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  }
});

// Create resume
const createResume = async (resumeData: ResumeCreate) => {
  try {
    const response = await apiClient.post('/resumes', resumeData);
    return response.data;
  } catch (error) {
    console.error('Error creating resume:', error.response?.data);
    throw error;
  }
};

// Optimize resume
const optimizeResume = async (resumeId: string, jobDescription: string) => {
  try {
    const response = await apiClient.post(`/resumes/${resumeId}/optimize`, {
      job_description: jobDescription
    });
    return response.data;
  } catch (error) {
    console.error('Error optimizing resume:', error.response?.data);
    throw error;
  }
};

// Upload and parse PDF
const parseResume = async (pdfFile: File) => {
  const formData = new FormData();
  formData.append('file', pdfFile);
  
  try {
    const response = await apiClient.post('/resumes/parse', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error parsing resume:', error.response?.data);
    throw error;
  }
};
```

### Python Examples

```python
import requests
import json

class CareerONAPI:
    def __init__(self, base_url="http://localhost:5000/api"):
        self.base_url = base_url
        self.token = None
    
    def login(self, email: str, password: str):
        response = requests.post(f"{self.base_url}/login", json={
            "email": email,
            "password": password
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            return data
        else:
            raise Exception(f"Login failed: {response.json()}")
    
    def _get_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
    
    def create_resume(self, user_id: str, title: str, summary: str):
        response = requests.post(f"{self.base_url}/resumes", 
            json={
                "user_id": user_id,
                "title": title,
                "summary": summary
            },
            headers=self._get_headers()
        )
        return response.json()
    
    def optimize_resume(self, resume_id: str, job_description: str):
        response = requests.post(f"{self.base_url}/resumes/{resume_id}/optimize",
            json={"job_description": job_description},
            headers=self._get_headers()
        )
        return response.json()
    
    def get_recommendations(self, user_id: str):
        response = requests.post(f"{self.base_url}/recommend",
            json={"user_id": user_id},
            headers=self._get_headers()
        )
        return response.json()

# Usage
api = CareerONAPI()
api.login("user@example.com", "password123")

# Create and optimize resume
resume = api.create_resume("user-id", "Software Engineer", "Experienced developer...")
optimization = api.optimize_resume(resume["id"], "Python developer job description...")
recommendations = api.get_recommendations("user-id")
```

---

**🚀 Ready to build amazing career tools? Start with our comprehensive API!**

For questions or support, please refer to the [GitHub repository](https://github.com/Skullybutcher/careerON) or create an issue.
