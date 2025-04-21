# Career Opportunities Navigator

## Project Overview
The Career Opportunities Navigator is a comprehensive resume management system that helps users create, optimize, and export professional resumes. The application provides:

- User account management
- Resume creation with multiple sections
- Resume parsing from PDF
- AI-powered resume optimization
- Professional resume exports in multiple formats

## Key Features

### Resume Management
- Create and manage multiple resumes
- Organize resume sections (personal info, education, experience, etc.)
- Customize section visibility and order

### Resume Processing
- Upload and parse existing resumes (PDF)
- AI-powered optimization based on job descriptions
- Export resumes in PDF/HTML with professional templates

### User Experience
- Secure authentication (JWT)
- Responsive web interface
- Real-time preview of resume changes

## Technology Stack

### Backend
- Python (Flask)
- SQLAlchemy (ORM)
- JWT Authentication
- Resume parsing libraries

### Frontend
- HTML5, CSS3, JavaScript
- Modern responsive design
- Interactive resume builder

### Database
- SQLite (Development)
- PostgreSQL (Production-ready)

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/career-opportunities-navigator.git
   cd career-opportunities-navigator
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Running the Application

### Development Server
```bash
flask run
```
The application will be available at `http://localhost:5000`

### Production Deployment
For production deployment, consider using:
- Gunicorn (WSGI server)
- Nginx (Reverse proxy)
- PostgreSQL (Database)

## Project Structure
```
career-opportunities-navigator/
├── api/                  # API routes and schemas
├── database/             # Database models and connection
├── services/             # Business logic services
├── static/               # Static files (CSS, JS)
├── templates/            # HTML templates
├── app.py                # Main application entry point
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## API Documentation
For detailed API documentation, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
