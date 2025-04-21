from flask import Blueprint, request, jsonify
from api.limiter import limiter
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import (
    User, Resume, PersonalInfo, Education, Experience, 
    Skill, Project, Achievement, Extracurricular, Course,
    Certification, VolunteerWork, Publication
)
from api.schemas import (
    UserCreate, UserResponse, ResumeCreate, ResumeResponse, 
    PersonalInfoSchema, EducationSchema, ExperienceSchema,
    SkillSchema, ProjectSchema, AchievementSchema, 
    ExtracurricularSchema, CourseSchema, CertificationSchema,
    VolunteerWorkSchema, PublicationSchema, ResumeOptimizeRequest,
    UserLogin
)
from services.resume_parser import ResumeParser
from services.resume_optimizer import ResumeOptimizer
from services.resume_generator import ResumeGenerator
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
from config import Config

# JWT Configuration
SECRET_KEY = Config.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

api = Blueprint('api', __name__)

@api.route("/test", methods=["GET"])
def test_endpoint():
    return jsonify({"message": "API is working"}), 200

resume_parser = ResumeParser()
resume_optimizer = ResumeOptimizer()
resume_generator = ResumeGenerator()

# User routes
@api.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    data = request.json
    
    # Validate input
    try:
        login_data = UserLogin(**data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    db = next(get_db())
    
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Verify password
    if not check_password_hash(user.password, login_data.password):
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Create JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return jsonify({
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user).dict()
    })

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@api.route("/users", methods=["POST"])
def create_user():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Validate input
    try:
        user_data = UserCreate(**data)
    except Exception as e:
        return jsonify({"error": f"Invalid user data: {str(e)}"}), 400
    
    db = next(get_db())
    
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            return jsonify({"error": "User with this email already exists"}), 409
        
        # Create new user
        hashed_password = generate_password_hash(user_data.password)
        user = User(
            id=str(uuid.uuid4()),
            name=user_data.name,
            email=user_data.email,
            password=hashed_password
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return jsonify(UserResponse.from_orm(user).dict()), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# Resume routes
@api.route("/resumes", methods=["POST"])
def create_resume():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        print("Received data:", data)  # Debug logging
        user_id = data.get("user_id")
    except Exception as e:
        return jsonify({"error": f"Invalid JSON: {str(e)}"}), 400
    
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    db = next(get_db())
    
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Parse request data
    try:
        resume_data = ResumeCreate(**data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    # Create default section settings if not provided
    if not resume_data.section_settings:
        default_sections = [
            {"name": "personal_info", "visible": True, "order": 1},
            {"name": "summary", "visible": True, "order": 2},
            {"name": "education", "visible": True, "order": 3},
            {"name": "experience", "visible": True, "order": 4},
            {"name": "skills", "visible": True, "order": 5},
            {"name": "projects", "visible": True, "order": 6},
            {"name": "achievements", "visible": True, "order": 7},
            {"name": "extracurriculars", "visible": True, "order": 8},
            {"name": "courses", "visible": True, "order": 9},
            {"name": "certifications", "visible": True, "order": 10},
            {"name": "volunteer_work", "visible": True, "order": 11},
            {"name": "publications", "visible": True, "order": 12}
        ]
        section_settings = default_sections
    else:
        section_settings = [section.dict() for section in resume_data.section_settings]
    
    # Create new resume
    resume = Resume(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title=resume_data.title,
        summary=resume_data.summary,
        section_settings=section_settings
    )
    
    db.add(resume)
    db.commit()
    db.refresh(resume)
    
    return jsonify(ResumeResponse.from_orm(resume).dict()), 201

@api.route("/users/<user_id>/resumes", methods=["GET"])
def get_user_resumes(user_id):
    db = next(get_db())
    
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get all resumes for the user
    resumes = db.query(Resume).filter(Resume.user_id == user_id).all()
    
    return jsonify([ResumeResponse.from_orm(resume).dict() for resume in resumes]), 200

@api.route("/resumes/<resume_id>", methods=["GET"])
def get_resume(resume_id):
    db = next(get_db())
    
    # Get resume
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        return jsonify({"error": "Resume not found"}), 404
    
    return jsonify(ResumeResponse.from_orm(resume).dict()), 200

@api.route("/resumes/<resume_id>", methods=["PUT"])
def update_resume(resume_id):
    data = request.json
    
    db = next(get_db())
    
    # Get resume
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        return jsonify({"error": "Resume not found"}), 404
    
    # Update resume fields
    if "title" in data:
        resume.title = data["title"]
    if "summary" in data:
        resume.summary = data["summary"]
    if "section_settings" in data:
        resume.section_settings = data["section_settings"]
    
    resume.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(resume)
    
    return jsonify(ResumeResponse.from_orm(resume).dict()), 200

@api.route("/resumes/<resume_id>", methods=["DELETE"])
def delete_resume(resume_id):
    db = next(get_db())
    
    # Get resume
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        return jsonify({"error": "Resume not found"}), 404
    
    # Delete resume
    db.delete(resume)
    db.commit()
    
    return "", 204

# Resume section routes (examples for a few sections)
@api.route("/resumes/<resume_id>/personal-info", methods=["POST", "PUT"])
def update_personal_info(resume_id):
    data = request.json
    
    db = next(get_db())
    
    # Check if resume exists
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        return jsonify({"error": "Resume not found"}), 404
    
    # Validate input
    try:
        personal_info_data = PersonalInfoSchema(**data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    # Update or create personal info
    personal_info = db.query(PersonalInfo).filter(PersonalInfo.resume_id == resume_id).first()
    
    if personal_info:
        # Update existing
        for key, value in personal_info_data.dict().items():
            setattr(personal_info, key, value)
    else:
        # Create new
        personal_info = PersonalInfo(
            id=str(uuid.uuid4()),
            resume_id=resume_id,
            **personal_info_data.dict()
        )
        db.add(personal_info)
    
    resume.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(personal_info)
    
    return jsonify(PersonalInfoSchema.from_orm(personal_info).dict()), 200

@api.route("/resumes/<resume_id>/education", methods=["POST"])
def add_education(resume_id):
    data = request.json
    
    db = next(get_db())
    
    # Check if resume exists
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        return jsonify({"error": "Resume not found"}), 404
    
    # Validate input
    try:
        education_data = EducationSchema(**data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    # Create new education
    education = Education(
        id=str(uuid.uuid4()),
        resume_id=resume_id,
        **education_data.dict()
    )
    
    db.add(education)
    resume.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(education)
    
    return jsonify(EducationSchema.from_orm(education).dict()), 201

@api.route("/resumes/<resume_id>/education/<education_id>", methods=["PUT"])
def update_education(resume_id, education_id):
    data = request.json
    
    db = next(get_db())
    
    # Get education
    education = db.query(Education).filter(
        Education.id == education_id,
        Education.resume_id == resume_id
    ).first()
    
    if not education:
        return jsonify({"error": "Education not found"}), 404
    
    # Validate input
    try:
        education_data = EducationSchema(**data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    # Update education
    for key, value in education_data.dict().items():
        setattr(education, key, value)
    
    education.resume.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(education)
    
    return jsonify(EducationSchema.from_orm(education).dict()), 200

@api.route("/resumes/<resume_id>/education/<education_id>", methods=["DELETE"])
def delete_education(resume_id, education_id):
    db = next(get_db())
    
    # Get education
    education = db.query(Education).filter(
        Education.id == education_id,
        Education.resume_id == resume_id
    ).first()
    
    if not education:
        return jsonify({"error": "Education not found"}), 404
    
    # Delete education
    db.delete(education)
    education.resume.updated_at = datetime.utcnow()
    db.commit()
    
    return "", 204

# Resume parsing routes
@api.route("/resumes/parse", methods=["POST"])
def parse_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    try:
        parsed_resume = resume_parser.parse_from_pdf(file)
        return jsonify(parsed_resume), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Resume optimization routes
@api.route("/resumes/<resume_id>/optimize", methods=["POST"])
def optimize_resume(resume_id):
    data = request.json
    
    # Validate input
    try:
        optimize_request = ResumeOptimizeRequest(**data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    db = next(get_db())
    
    # Get resume
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        return jsonify({"error": "Resume not found"}), 404
    
    # Convert to dict for optimizer
    resume_dict = ResumeResponse.from_orm(resume).dict()
    
    # Optimize resume
    try:
        optimization_result = resume_optimizer.optimize_for_job(
            resume_dict, 
            optimize_request.job_description
        )
        return jsonify(optimization_result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Resume export routes
@api.route("/resumes/<resume_id>/export", methods=["GET"])
def export_resume(resume_id):
    format_type = request.args.get("format", "pdf")
    template_name = request.args.get("template", "modern")
    
    db = next(get_db())
    
    # Get resume
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        return jsonify({"error": "Resume not found"}), 404
    
    # Convert to dict for generator
    resume_dict = ResumeResponse.from_orm(resume).dict()
    
    try:
        if format_type == "pdf":
            pdf_bytes = resume_generator.generate_pdf(resume_dict, template_name)
            return current_app.response_class(
                pdf_bytes,
                mimetype='application/pdf',
                headers={"Content-Disposition": f"attachment;filename={resume.title}.pdf"}
            )
        elif format_type == "html":
            html = resume_generator.generate_html(resume_dict, template_name)
            return html
        else:
            return jsonify({"error": "Unsupported format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
