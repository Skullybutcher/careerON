# Career Opportunities Navigator API Documentation
**Version**: 1.0.0  
**Last Updated**: 2023-11-15

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
All endpoints are prefixed with: `https://api.careernavigator.example.com/api/v1`

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
| PUT    | `/resumes/{resume_id}` | Update resume |
| DELETE | `/resumes/{resume_id}` | Delete resume |

**Sample Create Request**:
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

## Resume Section Management

### Common Section Structure
All section endpoints:
- Use `resume_id` in path
- Return 204 for DELETE
- Use same error codes (401, 404)

**Available Sections**:
## Available Resume Sections

### Personal Info
**Fields**:
- full_name
- email
- phone
- location
- linkedin_url
- github_url
- portfolio_url

### Summary
**Fields**:
- content (professional summary/objective)

### Education
**Fields**:
- institution
- degree
- field_of_study
- start_date
- end_date
- gpa
- description

### Experience
**Fields**:
- company
- position
- location
- start_date
- end_date
- current (boolean)
- description
- achievements

### Skills
**Fields**:
- name
- category (technical, soft, etc.)
- proficiency (beginner, intermediate, expert)
- years_of_experience

### Projects
**Fields**:
- title
- description
- technologies
- start_date
- end_date
- url

### Achievements
**Fields**:
- title
- description
- date
- issuer

### Extracurriculars
**Fields**:
- activity_name
- organization
- role
- start_date
- end_date
- description

### Courses
**Fields**:
- course_name
- institution
- completion_date
- description

### Certifications
**Fields**:
- name
- issuing_organization
- issue_date
- credential_id
- credential_url

### Volunteer Work
**Fields**:
- organization
- role
- start_date
- end_date
- description

### Publications
**Fields**:
- title
- authors
- publication_venue
- publication_date
- url
- description

**Sample Education Update**:
```json
{
  "institution": "MIT",
  "degree": "BSc Computer Science",
  "gpa": 3.8,
  "description": "Specialized in AI"
}
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

**Response**:
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

**Response**:  
PDF file with `Content-Disposition: attachment` header

## Error Handling

**Common Error Codes**:
- `400 Bad Request`: Invalid data
- `401 Unauthorized`: Missing/invalid token
- `404 Not Found`: Resource doesn't exist
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
