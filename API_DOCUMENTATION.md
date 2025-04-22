# Career Opportunities Navigator API Documentation
**Version**: 1.0.0  
**Last Updated**: 2024-06-01

## Table of Contents
1. [Introduction](#introduction)
2. [Authentication](#authentication)
3. [Base URL](#base-url)
4. [Versioning](#versioning)
5. [User Management](#user-management)
6. [Resume Management](#resume-management)
7. [Resume Section Management](#resume-section-management)
8. [Resume Processing](#resume-processing)
9. [Error Handling](#error-handling)
10. [Test Endpoint](#test-endpoint)

## Introduction
This API powers the Career Opportunities Navigator application, providing endpoints for:
- User account management
- Resume creation and management
- Resume section management
- Resume processing (parsing, optimization, export)

## Authentication
All endpoints (except `/users` and `/login`) require JWT authentication. Include the token in the Authorization header:

```http
Authorization: Bearer {your_token}
```

Tokens are obtained by:
1. Registering via `POST /users`
2. Logging in via `POST /login`

## Base URL
All endpoints are prefixed with: `https://localhost:5000/api`

## Versioning
API version is included in the base URL. Breaking changes will increment the version number (v1 → v2).

## User Management

### Register User
`POST /users`

**Request**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**Success Response (201)**:
```json
{
  "id": "usr_123",
  "name": "John Doe",
  "email": "john@example.com",
  "created_at": "2023-11-15T10:00:00Z"
}
```

**Errors**:
- `400 Bad Request`: Invalid data
- `409 Conflict`: Email exists

## Resume Management

### Resume Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/resumes` | Create new resume |
| GET    | `/users/{user_id}/resumes` | List user's resumes |
| GET    | `/resumes/{resume_id}` | Get resume details |
| DELETE | `/resumes/{resume_id}` | Delete resume |

### Create Resume
`POST /resumes`

**Request**:
```json
{
  "user_id": "usr_123",
  "title": "Software Engineer Resume",
  "summary": "5+ years experience in full-stack development",
  "section_settings": [
    {
      "name": "education",
      "visible": true,
      "order": 1
    }
  ]
}
```

**Success Response (201)**:
```json
{
  "id": "res_456",
  "user_id": "usr_123",
  "title": "Software Engineer Resume",
  "summary": "5+ years experience in full-stack development",
  "section_settings": [
    {
      "name": "education",
      "visible": true,
      "order": 1
    }
  ],
  "created_at": "2024-06-01T12:00:00Z"
}
```

### Get User's Resumes
`GET /users/{user_id}/resumes`

**Success Response (200)**:
```json
[
  {
    "id": "res_456",
    "title": "Software Engineer Resume",
    "summary": "5+ years experience in full-stack development",
    "section_settings": [...],
    "personal_info": {...}
  },
  ...
]
```

### Get Resume Details
`GET /resumes/{resume_id}`

**Success Response (200)**:
```json
{
  "id": "res_456",
  "user_id": "usr_123",
  "title": "Software Engineer Resume",
  "summary": "5+ years experience in full-stack development",
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
  "publications": [...]
}
```

### Delete Resume
`DELETE /resumes/{resume_id}`

**Success Response (200)**:
```json
{
  "message": "Resume deleted successfully"
}
```

## Resume Section Management

### Common Section Structure
All section endpoints:
- Use `resume_id` in path
- Support `GET` to retrieve section data
- Support `PUT` to update section data
- Return `404` if resume or section not found
- Return `400` for invalid data
- Return `500` for server errors

### Available Sections and Fields

#### Personal Info
`GET /resumes/{resume_id}/sections/personal_info`  
`PUT /resumes/{resume_id}/sections/personal_info`

**Fields**:
- full_name
- email
- phone
- location
- linkedin_url
- github_url
- portfolio_url

**PUT Request Example**:
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "123-456-7890",
  "location": "San Francisco, CA",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "github_url": "https://github.com/johndoe",
  "portfolio_url": "https://johndoe.com"
}
```

**Success Response (200)**:
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "123-456-7890",
  "location": "San Francisco, CA",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "github_url": "https://github.com/johndoe",
  "portfolio_url": "https://johndoe.com"
}
```

#### Summary
`GET /resumes/{resume_id}/sections/summary`  
`PUT /resumes/{resume_id}/sections/summary`

**Fields**:
- summary (string)

**PUT Request Example**:
```json
{
  "summary": "Experienced software engineer with expertise in full-stack development."
}
```

**Success Response (200)**:
```json
{
  "summary": "Experienced software engineer with expertise in full-stack development."
}
```

#### Education
`GET /resumes/{resume_id}/sections/education`  
`PUT /resumes/{resume_id}/sections/education`

**Fields**:
- institution
- degree
- field_of_study
- start_date (YYYY-MM-DD)
- end_date (YYYY-MM-DD)
- gpa
- description

**PUT Request Example**:
```json
[
  {
    "institution": "MIT",
    "degree": "BSc Computer Science",
    "field_of_study": "Computer Science",
    "start_date": "2015-09-01",
    "end_date": "2019-06-01",
    "gpa": 3.8,
    "description": "Specialized in AI"
  }
]
```

**Success Response (200)**:
```json
[
  {
    "institution": "MIT",
    "degree": "BSc Computer Science",
    "field_of_study": "Computer Science",
    "start_date": "2015-09-01",
    "end_date": "2019-06-01",
    "gpa": 3.8,
    "description": "Specialized in AI"
  }
]
```

#### Experience
`GET /resumes/{resume_id}/sections/experience`  
`PUT /resumes/{resume_id}/sections/experience`

**Fields**:
- company
- position
- location
- start_date (YYYY-MM-DD)
- end_date (YYYY-MM-DD)
- current (boolean)
- description
- achievements

**PUT Request Example**:
```json
[
  {
    "company": "Tech Corp",
    "position": "Software Engineer",
    "location": "San Francisco, CA",
    "start_date": "2019-07-01",
    "end_date": "2023-05-01",
    "current": false,
    "description": "Developed web applications",
    "achievements": "Employee of the Year 2021"
  }
]
```

**Success Response (200)**:
```json
[
  {
    "company": "Tech Corp",
    "position": "Software Engineer",
    "location": "San Francisco, CA",
    "start_date": "2019-07-01",
    "end_date": "2023-05-01",
    "current": false,
    "description": "Developed web applications",
    "achievements": "Employee of the Year 2021"
  }
]
```

#### Skills
`GET /resumes/{resume_id}/sections/skills`  
`PUT /resumes/{resume_id}/sections/skills`

**Fields**:
- name
- category (technical, soft, etc.)
- proficiency (beginner, intermediate, expert)
- years_of_experience

**PUT Request Example**:
```json
[
  {
    "name": "Python",
    "category": "Technical",
    "proficiency": "Expert",
    "years_of_experience": 5
  }
]
```

**Success Response (200)**:
```json
[
  {
    "name": "Python",
    "category": "Technical",
    "proficiency": "Expert"
  }
]
```

#### Projects
`GET /resumes/{resume_id}/sections/projects`  
`PUT /resumes/{resume_id}/sections/projects`

**Fields**:
- title
- description
- technologies
- start_date (YYYY-MM-DD)
- end_date (YYYY-MM-DD)
- url

**PUT Request Example**:
```json
[
  {
    "title": "Project X",
    "description": "A web app for X",
    "technologies": ["React", "Node.js"],
    "start_date": "2021-01-01",
    "end_date": "2021-12-31",
    "url": "https://projectx.example.com"
  }
]
```

**Success Response (200)**:
```json
[
  {
    "title": "Project X",
    "description": "A web app for X",
    "technologies": ["React", "Node.js"],
    "start_date": "2021-01-01",
    "end_date": "2021-12-31",
    "url": "https://projectx.example.com"
  }
]
```

## Resume Processing

### Parse Resume
`POST /resumes/parse`

**Request**:  
Send PDF as form-data with key `resume_file`

**Response**:
```json
{
  "personal_info": {
    "name": "John Doe",
    "email": "john@example.com"
  },
  "education": [
    {
      "institution": "MIT",
      "degree": "BSc Computer Science"
    }
  ]
}
```

### Optimize Resume
`POST /resumes/{resume_id}/optimize`

**Request**:
```json
{
  "job_description": "Looking for Python developer with 5+ years experience...",
  "optimization_level": "aggressive"
}
```

**Success Response (200)**:
```json
{
  "score": 87.5,
  "suggestions": [
    "Add more Python-specific keywords",
    "Highlight AWS experience"
  ]
}
```

### Export Resume
`GET /resumes/{resume_id}/export?format=pdf&template=modern`

**Query Parameters**:
- `format` (optional): Export format, currently only `pdf` supported (default: `pdf`)
- `template` (optional): Template to use for export, e.g., `modern` or `default` (default: `default`)

**Response**:  
PDF file with `Content-Disposition: attachment` header

## Test Endpoint

### Check API Status
`GET /test`

**Success Response (200)**:
```json
{
  "message": "API is working"
}
```

## Error Handling

**Common Error Codes**:
- `400 Bad Request`: Invalid data
- `401 Unauthorized`: Missing/invalid token
- `404 Not Found`: Resource doesn't exist
- `409 Conflict`: Conflict such as duplicate user
- `500 Server Error`: Internal server error

**Error Response Format**:
```json
{
  "error": "not_found",
  "message": "Resume not found",
  "details": {
    "resume_id": "res_456"
  }
}
