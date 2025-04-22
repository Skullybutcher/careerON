from flask import Blueprint, request, jsonify, current_app
from flask_cors import CORS
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
CORS(api, origins=["http://localhost:8080"])

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

@api.route("/resumes/<resume_id>", methods=["GET"])
def get_resume(resume_id):
    try:
        db = next(get_db())
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            return jsonify({"error": "Resume not found"}), 404
        
        from api.schemas import ResumeResponse, PersonalInfoSchema
        try:
            if resume.personal_info:
                resume.personal_info = PersonalInfoSchema.from_orm(resume.personal_info)
        except Exception as e:
            current_app.logger.error(f"Error serializing personal_info for resume {resume.id}: {str(e)}")
            resume.personal_info = None
        
        return jsonify(ResumeResponse.from_orm(resume).dict()), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching resume {resume_id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@api.route("/users/<user_id>/resumes", methods=["GET"])
def get_user_resumes(user_id):
    import traceback
    try:
        db = next(get_db())
        
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get all resumes for the user
        resumes = db.query(Resume).filter(Resume.user_id == user_id).all()
        
        # Convert personal_info ORM to Pydantic model for each resume with error handling and detailed logging
        from api.schemas import ResumeResponse, PersonalInfoSchema
        serialized_resumes = []
        for resume in resumes:
            try:
                current_app.logger.debug(f"Serializing resume {resume.id} with data: {resume.__dict__}")
                personal_info_data = None
                if resume.personal_info:
                    current_app.logger.debug(f"Serializing personal_info for resume {resume.id} with data: {resume.personal_info.__dict__}")
                    personal_info_data = PersonalInfoSchema.from_orm(resume.personal_info).dict()
            except Exception as e:
                current_app.logger.error(f"Error serializing personal_info for resume {resume.id}: {str(e)}")
                current_app.logger.error(traceback.format_exc())
                personal_info_data = None
            try:
                resume_dict = ResumeResponse.from_orm(resume).dict()
                resume_dict['personal_info'] = personal_info_data
                serialized_resumes.append(resume_dict)
            except Exception as e:
                current_app.logger.error(f"Error serializing resume {resume.id}: {str(e)}")
                current_app.logger.error(traceback.format_exc())
        
        return jsonify(serialized_resumes), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching resumes for user {user_id}: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500
# Resume section routes

from api.schemas import (
    PersonalInfoSchema, EducationSchema, ExperienceSchema,
    SkillSchema, ProjectSchema
)

@api.route("/resumes/<resume_id>/sections/personal_info", methods=["GET", "PUT"])
def personal_info_section(resume_id):
    db = next(get_db())
    if request.method == "GET":
        try:
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if not resume or not resume.personal_info:
                return jsonify({"error": "Personal info not found"}), 404
            personal_info = PersonalInfoSchema.from_orm(resume.personal_info)
            return jsonify(personal_info.dict()), 200
        except Exception as e:
            current_app.logger.error(f"Error fetching personal info for resume {resume_id}: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    elif request.method == "PUT":
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            # Validate input
            personal_info_data = PersonalInfoSchema(**data)
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if not resume:
                return jsonify({"error": "Resume not found"}), 404
            # Update or create personal_info
            if resume.personal_info:
                for key, value in personal_info_data.dict().items():
                    setattr(resume.personal_info, key, value)
            else:
                from database.models import PersonalInfo
                new_personal_info = PersonalInfo(**personal_info_data.dict())
                resume.personal_info = new_personal_info
                db.add(new_personal_info)
            db.commit()
            return jsonify(personal_info_data.dict()), 200
        except Exception as e:
            current_app.logger.error(f"Error updating personal info for resume {resume_id}: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

@api.route("/resumes/<resume_id>/sections/summary", methods=["GET", "PUT"])
def summary_section(resume_id):
    db = next(get_db())
    if request.method == "GET":
        try:
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if not resume or not resume.summary:
                return jsonify({"error": "Summary not found"}), 404
            return jsonify({"summary": resume.summary}), 200
        except Exception as e:
            current_app.logger.error(f"Error fetching summary for resume {resume_id}: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    elif request.method == "PUT":
        try:
            data = request.get_json()
            if not data or "summary" not in data:
                return jsonify({"error": "No summary provided"}), 400
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if not resume:
                return jsonify({"error": "Resume not found"}), 404
            resume.summary = data["summary"]
            db.commit()
            return jsonify({"summary": resume.summary}), 200
        except Exception as e:
            current_app.logger.error(f"Error updating summary for resume {resume_id}: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

@api.route("/resumes/<resume_id>/sections/education", methods=["GET", "PUT"])
def education_section(resume_id):
    db = next(get_db())
    if request.method == "GET":
        try:
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if not resume:
                return jsonify({"error": "Resume not found"}), 404
            education_list = resume.education or []
            education_schema = [EducationSchema.from_orm(edu).dict() for edu in education_list]
            return jsonify(education_schema), 200
        except Exception as e:
            current_app.logger.error(f"Error fetching education for resume {resume_id}: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    elif request.method == "PUT":
        try:
            data = request.get_json()
            if not data or not isinstance(data, list):
                return jsonify({"error": "Invalid data provided"}), 400
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if not resume:
                return jsonify({"error": "Resume not found"}), 404
            from database.models import Education
            # Clear existing education entries
            resume.education.clear()
            # Add new education entries
            for edu_data in data:
                edu_obj = Education(**edu_data)
                resume.education.append(edu_obj)
                db.add(edu_obj)
            db.commit()
            education_schema = [EducationSchema.from_orm(edu).dict() for edu in resume.education]
            return jsonify(education_schema), 200
        except Exception as e:
            current_app.logger.error(f"Error updating education for resume {resume_id}: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

@api.route("/resumes/<resume_id>/sections/experience", methods=["GET", "PUT"])
def experience_section(resume_id):
    db = next(get_db())
    if request.method == "GET":
        try:
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if not resume:
                return jsonify({"error": "Resume not found"}), 404
            experience_list = resume.experience
            if experience_list is None:
                experience_list = []
            if not isinstance(experience_list, list):
                experience_list = list(experience_list)
            experience_schema = []
            for exp in experience_list:
                try:
                    experience_schema.append(ExperienceSchema.from_orm(exp).dict())
                except Exception as inner_e:
                    current_app.logger.error(f"Error serializing experience entry for resume {resume_id}: {str(inner_e)}")
            return jsonify(experience_schema), 200
        except Exception as e:
            current_app.logger.error(f"Error fetching experience for resume {resume_id}: {str(e)}", exc_info=True)
            return jsonify({"error": "Internal server error"}), 500
    elif request.method == "PUT":
        try:
            data = request.get_json()
            if not data or not isinstance(data, list):
                return jsonify({"error": "Invalid data provided"}), 400
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if not resume:
                return jsonify({"error": "Resume not found"}), 404
            from database.models import Experience
            # Clear existing experience entries
            resume.experience.clear()
            # Add new experience entries
            for exp_data in data:
                exp_obj = Experience(**exp_data)
                resume.experience.append(exp_obj)
                db.add(exp_obj)
            db.commit()
            experience_schema = [ExperienceSchema.from_orm(exp).dict() for exp in resume.experience]
            return jsonify(experience_schema), 200
        except Exception as e:
            current_app.logger.error(f"Error updating experience for resume {resume_id}: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

@api.route("/resumes/<resume_id>/sections/skills", methods=["GET", "PUT"])
def skills_section(resume_id):
    import traceback
    db = next(get_db())
    if request.method == "GET":
        try:
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if not resume:
                return jsonify({"error": "Resume not found"}), 404
            skills_list = resume.skills or []
            skills_schema = [SkillSchema.from_orm(skill).dict() for skill in skills_list]
            return jsonify(skills_schema), 200
        except Exception as e:
            current_app.logger.error(f"Error fetching skills for resume {resume_id}: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    elif request.method == "PUT":
        try:
            data = request.get_json()
            if not data or not isinstance(data, list):
                return jsonify({"error": "Invalid data provided"}), 400
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if not resume:
                return jsonify({"error": "Resume not found"}), 404
            from database.models import Skill
            # Clear existing skills entries
            resume.skills.clear()
            # Add new skills entries
            for skill_data in data:
                # Map 'proficiency' to 'level' and remove 'years_of_experience' if present
                if 'proficiency' in skill_data:
                    skill_data['level'] = skill_data.pop('proficiency')
                if 'years_of_experience' in skill_data:
                    skill_data.pop('years_of_experience')
                skill_obj = Skill(**skill_data)
                resume.skills.append(skill_obj)
                db.add(skill_obj)
            db.commit()
            skills_schema = [SkillSchema.from_orm(skill).dict() for skill in resume.skills]
            return jsonify(skills_schema), 200
        except Exception as e:
            current_app.logger.error(f"Error updating skills for resume {resume_id}: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            return jsonify({"error": "Internal server error"}), 500

@api.route("/resumes/<resume_id>/sections/projects", methods=["GET", "PUT"])
def projects_section(resume_id):
    db = next(get_db())
    if request.method == "GET":
        try:
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if not resume:
                return jsonify({"error": "Resume not found"}), 404
            projects_list = resume.projects or []
            projects_schema = [ProjectSchema.from_orm(proj).dict() for proj in projects_list]
            return jsonify(projects_schema), 200
        except Exception as e:
            current_app.logger.error(f"Error fetching projects for resume {resume_id}: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    elif request.method == "PUT":
        try:
            data = request.get_json()
            if not data or not isinstance(data, list):
                return jsonify({"error": "Invalid data provided"}), 400
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if not resume:
                return jsonify({"error": "Resume not found"}), 404
            from database.models import Project
            # Clear existing projects entries
            resume.projects.clear()
            # Add new projects entries
            from datetime import datetime
            for proj_data in data:
                # Map 'url' to 'link'
                if 'url' in proj_data:
                    proj_data['link'] = proj_data.pop('url')
                # Convert start_date and end_date strings to date objects or None
                if 'start_date' in proj_data and proj_data['start_date']:
                    try:
                        proj_data['start_date'] = datetime.strptime(proj_data['start_date'], '%Y-%m-%d').date()
                    except Exception:
                        proj_data['start_date'] = None
                else:
                    proj_data['start_date'] = None
                if 'end_date' in proj_data and proj_data['end_date']:
                    try:
                        proj_data['end_date'] = datetime.strptime(proj_data['end_date'], '%Y-%m-%d').date()
                    except Exception:
                        proj_data['end_date'] = None
                else:
                    proj_data['end_date'] = None
                proj_obj = Project(**proj_data)
                resume.projects.append(proj_obj)
                db.add(proj_obj)
            db.commit()
            projects_schema = [ProjectSchema.from_orm(proj).dict() for proj in resume.projects]
            return jsonify(projects_schema), 200
        except Exception as e:
            import traceback
            current_app.logger.error(f"Error updating projects for resume {resume_id}: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            return jsonify({"error": "Internal server error"}), 500
