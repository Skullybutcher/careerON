# CareerON Project - Requirements.txt Analysis

## Overview
After scanning all Python source files in the careerON project, I have generated a complete and minimal `requirements.txt` file containing only the external dependencies actually used in the codebase.

## Files Analyzed
- **Root files**: `app.py`, `config.py`, `setup.sh`
- **API module**: `api/limiter.py`, `api/routes.py`, `api/schemas.py`, `api/job_recommendation.py`
- **Services module**: `services/resume_generator.py`, `services/resume_optimizer.py`, `services/resume_parser.py`
- **Database module**: `database/db.py`, `database/models.py`
- **Utils module**: `utils/linkedin_ws.py`

## Key Dependencies Identified

### Core Web Framework
- **Flask**: Main web framework
- **Flask-Cors**: CORS handling for frontend integration
- **Flask-Limiter**: Rate limiting functionality
- **Werkzeug**: WSGI utilities (security functions)

### Database & ORM
- **SQLAlchemy**: ORM for database operations
- **psycopg2-binary**: PostgreSQL adapter

### Data Validation & Serialization
- **Pydantic**: Data validation and serialization
- **email_validator**: Email validation for Pydantic

### Authentication & Security
- **PyJWT**: JWT token handling
- **python-dotenv**: Environment variable management

### PDF Processing
- **PyPDF2**: PDF text extraction
- **PyMuPDF**: Advanced PDF operations (imported as `fitz`)
- **pdfkit**: HTML to PDF conversion

### Natural Language Processing
- **spacy**: Advanced NLP operations
- **sentence-transformers**: Text embeddings for similarity matching
- **en_core_web_sm**: spaCy English language model

### Machine Learning & AI
- **torch**: PyTorch for deep learning models
- **google-genai**: Google Generative AI integration

### Text Processing
- **rapidfuzz**: Fast fuzzy string matching

### OCR & Computer Vision
- **easyocr**: Optical Character Recognition for scanned PDFs

### Web Scraping
- **selenium**: Web automation for LinkedIn scraping
- **webdriver-manager**: Chrome driver management
- **beautifulsoup4**: HTML parsing

### HTTP & Utilities
- **requests**: HTTP client library
- **Jinja2**: Template engine for HTML generation
- **python-dateutil**: Date/time utilities

## Changes Made
1. **Removed 100+ unused packages** from the original requirements.txt
2. **Preserved exact versions** where they were already pinned and working
3. **Used compatible versions** for packages where specific versions weren't critical
4. **Maintained Python 3.10+ compatibility**
5. **Organized dependencies by category** for better maintainability

## Version Considerations
- All selected versions are compatible with Python 3.10+
- Versions are chosen to avoid known security vulnerabilities
- Dependencies are compatible with each other
- Maintained stable versions for production use

## Excluded Packages
Removed development-only, testing, and unused packages including:
- Jupyter notebook dependencies
- Unused data science libraries (pandas, numpy, scikit-learn, etc.)
- Development tools not used in production
- Duplicate or obsolete packages
- Platform-specific packages not needed

This minimal requirements.txt reduces installation time, disk space, and potential security vulnerabilities while maintaining full functionality of the careerON application.