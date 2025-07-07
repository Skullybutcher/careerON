# careerON
*AI-Powered Resume Builder & Job Matching Platform*

## Overview

careerON is a comprehensive AI-powered career platform that revolutionizes the job search process by combining intelligent resume building, optimization, and personalized job matching. The platform helps job seekers create ATS-compliant resumes, optimize them for specific job descriptions, and discover relevant opportunities through advanced AI algorithms.

**Key Features:**
- 🤖 AI-powered resume optimization using advanced language models
- 📄 Intelligent PDF resume parsing with NLP heuristics
- 🎯 Personalized job recommendations and matching
- 📊 ATS compatibility analysis and scoring
- 🎨 Professional resume templates with PDF export
- 👤 Secure user authentication and profile management
- 📱 Modern, responsive web interface

**Architecture:**
```
Frontend (React/TypeScript) ↔ Flask REST API ↔ PostgreSQL Database
                                      ↕
              AI Services: NVIDIA API | spaCy | SentenceTransformers | PyMuPDF
```

## Table of Contents

- [Tech Stack](#tech-stack)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [API Usage](#api-usage)
- [Testing](#testing)
- [Linting & Formatting](#linting--formatting)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Contact & Acknowledgments](#contact--acknowledgments)

## Tech Stack

### Backend
- **Python 3.10+** - Core backend language
- **Flask** - Web framework with CORS support
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Primary database
- **PyJWT** - JWT authentication
- **PyMuPDF (fitz)** - PDF parsing and processing
- **spaCy** - Natural language processing
- **SentenceTransformers** - Semantic similarity analysis
- **NVIDIA API** - AI-powered text generation and optimization
- **BeautifulSoup4** - Web scraping capabilities
- **Selenium** - Automated job scraping
- **Flask-Limiter** - API rate limiting

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool and development server
- **Shadcn/ui** - Modern component library
- **Radix UI** - Accessible component primitives
- **TailwindCSS** - Utility-first CSS framework
- **React Hook Form** - Form management
- **Axios** - HTTP client
- **React Router** - Client-side routing
- **Zod** - Runtime type validation

### DevOps & Tools
- **pytest** - Testing framework
- **ESLint** - JavaScript/TypeScript linting
- **Flake8** - Python code linting
- **MyPy** - Python static type checking

## Features

### 🗂️ Resume Management
- Create and manage multiple professional resumes
- Drag-and-drop interface for section reordering
- Toggle visibility for specific resume sections
- Real-time preview and editing capabilities

### 📄 Intelligent PDF Parsing
- Upload existing PDF resumes for automatic data extraction
- Advanced NLP heuristics for accurate information parsing
- Structured data extraction: personal info, education, skills, projects
- Support for various resume formats and layouts

### 🧠 AI-Powered Optimization
- **Smart Job Matching**: Paste job descriptions for instant analysis
- **Match Scoring**: Quantified compatibility scores
- **Keyword Analysis**: Identification of missing critical keywords
- **Content Enhancement**: AI-generated summary improvements
- **Section-wise Recommendations**: Targeted advice for skills, projects, and experience
- **Resume Boost**: Job-specific content suggestions

### 🎨 Professional Templates & Export
- Multiple professional resume templates (default, modern)
- High-quality PDF export with custom styling
- ATS-compliant formatting
- Print-ready layouts

### 🔍 Job Discovery & Recommendations
- Automated job scraping from multiple sources
- AI-powered job matching based on user profiles
- Personalized recommendations using machine learning
- Location-based job filtering

### 🛡️ Security & Authentication
- Secure JWT-based authentication system
- Rate limiting for API protection
- User profile management
- Data privacy and security compliance

## Getting Started

### Prerequisites

Ensure you have the following installed:
- **Python 3.10+**
- **Node.js 18+** and npm
- **PostgreSQL 12+**
- **Git**

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Skullybutcher/careerON.git
cd careerON
```

2. **Set up the backend:**
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm
```

3. **Set up the frontend:**
```bash
cd frontend
npm install
cd ..
```

4. **Run setup script:**
```bash
bash setup.sh
```

### Environment Configuration

Create a `.env` file in the root directory with the following variables:

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_jwt_secret_key_here

# Database Configuration
SQLALCHEMY_DATABASE_URI=postgresql://username:password@localhost:5432/career_navigator

# AI Services
NVIDIA_API_KEY=your_nvidia_api_key_here
NVIDIA_API_URL=https://integrate.api.nvidia.com/v1/chat/completions
HF_TOKEN=your_huggingface_token_here

# Performance
DEVICE=cpu  # or 'gpu' if available

# Optional: Job Scraping
SCRAPER_API_KEY=your_scraper_api_key
```

**Required Environment Variables:**
- `SECRET_KEY` - JWT token signing key
- `SQLALCHEMY_DATABASE_URI` - PostgreSQL connection string
- `NVIDIA_API_KEY` - NVIDIA API for AI features
- `HF_TOKEN` - Hugging Face token for ML models

### Database Setup

1. **Create PostgreSQL database:**
```bash
createdb career_navigator
# Or using psql:
psql -U postgres -c "CREATE DATABASE career_navigator;"
```

2. **Database tables will be created automatically** when the application starts.

## Running the Application

### Backend Server
```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Start Flask development server
python app.py
# Or alternatively:
flask run
```
The backend will be available at `http://localhost:5000`

### Frontend Development Server
```bash
cd frontend
npm run dev
```
The frontend will be available at `http://localhost:8080`

### Production Build
```bash
# Build frontend for production
cd frontend
npm run build
cd ..

# The Flask server can serve the built frontend
python app.py
```

## API Usage

The API provides comprehensive endpoints for resume management, optimization, and job recommendations.

**Base URL:** `http://localhost:5000/api`

### Authentication Example
```bash
# Login and get JWT token
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Resume Optimization Example
```bash
# Optimize resume for a job description
curl -X POST http://localhost:5000/api/resumes/{resume_id}/optimize \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_jwt_token" \
  -d '{"job_description": "Senior Software Engineer with Python and React experience..."}'
```

### Job Recommendations Example
```bash
# Get personalized job recommendations
curl -X POST http://localhost:5000/api/recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_jwt_token" \
  -d '{"user_id": "your_user_id"}'
```

**� Full API Documentation:** See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for complete endpoint reference.

## Testing

Run the test suite to ensure everything is working correctly:

```bash
# Run all tests with coverage
pytest --cov=. --cov-report=html

# Run specific test modules
pytest tests/test_resume_parser.py
pytest tests/test_api.py

# View coverage report
open htmlcov/index.html  # On macOS
# Or navigate to htmlcov/index.html in your browser
```

## Linting & Formatting

### Python (Backend)
```bash
# Code linting
flake8 .

# Type checking
mypy .

# Format code (if using black)
black .
```

### TypeScript/JavaScript (Frontend)
```bash
cd frontend

# Lint frontend code
npm run lint

# Fix linting issues
npm run lint:fix
```

## Project Structure

```
careerON/
├── 📁 api/                    # Flask API routes and schemas
│   ├── routes.py             # Main API endpoints
│   ├── schemas.py            # Pydantic data validation schemas
│   ├── job_recommendation.py # Job matching algorithms
│   └── limiter.py            # Rate limiting configuration
├── 📁 database/              # Database models and configuration
│   ├── models.py             # SQLAlchemy ORM models
│   └── db.py                 # Database connection setup
├── 📁 services/              # Core business logic
│   ├── resume_parser.py      # PDF parsing and NLP processing
│   ├── resume_generator.py   # PDF generation and templating
│   └── resume_optimizer.py   # AI-powered optimization
├── 📁 frontend/              # React TypeScript frontend
│   ├── src/                  # Source code
│   ├── public/               # Static assets
│   ├── package.json          # Node.js dependencies
│   └── tailwind.config.ts    # TailwindCSS configuration
├── 📁 templates/             # HTML resume templates
├── 📁 static/                # CSS/JS static assets
├── 📁 utils/                 # Utility functions and helpers
├── 📄 app.py                 # Flask application entry point
├── 📄 config.py              # Environment configuration
├── 📄 requirements.txt       # Python dependencies
├── 📄 setup.sh              # Automated setup script
├── 📄 API_DOCUMENTATION.md  # Comprehensive API docs
└── 📄 README.md             # This file
```

## Contributing

We welcome contributions to careerON! Here's how to get started:

### Development Workflow

1. **Fork the repository** on GitHub
2. **Clone your fork:**
   ```bash
   git clone https://github.com/your-username/careerON.git
   cd careerON
   ```
3. **Create a feature branch:**
   ```bash
   git checkout -b feature/amazing-feature
   ```
4. **Make your changes** and ensure they follow our coding standards
5. **Run tests:**
   ```bash
   pytest --cov=.
   cd frontend && npm run lint
   ```
6. **Commit your changes:**
   ```bash
   git commit -m "Add amazing feature"
   ```
7. **Push to your branch:**
   ```bash
   git push origin feature/amazing-feature
   ```
8. **Open a Pull Request** with a clear description of your changes

### Code Standards
- Follow PEP 8 for Python code
- Use TypeScript for frontend development
- Write tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## Contact & Acknowledgments

### Contact
- **GitHub:** [Skullybutcher](https://github.com/Skullybutcher)
- **Issues:** [Report bugs or request features](https://github.com/Skullybutcher/careerON/issues)
- **Discussions:** [Join the community discussion](https://github.com/Skullybutcher/careerON/discussions)

### Acknowledgments

careerON is built with amazing open-source technologies:

- **AI & ML:** NVIDIA API, Hugging Face Transformers, spaCy, SentenceTransformers
- **Backend:** Flask, SQLAlchemy, PyMuPDF
- **Frontend:** React, TypeScript, Shadcn/ui, TailwindCSS
- **Database:** PostgreSQL
- **Development:** Vite, pytest, ESLint

Special thanks to the open-source community for providing the tools that make this project possible.

---

**Built with ❤️ for job seekers everywhere. Happy job hunting! 🚀**
