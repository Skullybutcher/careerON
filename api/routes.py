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

from flask import send_file
import io

@api.route("/resumes/<resume_id>/export", methods=["GET", "OPTIONS"])
def export_resume(resume_id):
    from flask import make_response
    import traceback
    try:
        # Handle CORS preflight
        if request.method == "OPTIONS":
            response = make_response('', 204)
            response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
            response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response

        export_format = request.args.get("format", "pdf")
        template = request.args.get("template", "default")

        if export_format != "pdf":
            response = make_response(jsonify({"error": "Unsupported export format"}), 400)
            response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
            return response

        from flask import render_template
        import pdfkit
        import datetime

        db = next(get_db())
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            response = make_response(jsonify({"error": "Resume not found"}), 404)
            response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
            return response

        # Determine visible sections from resume.section_settings
        visible_sections = set()
        if resume.section_settings:
            for section in resume.section_settings:
                if section.get("visible", True):
                    visible_sections.add(section.get("name"))

        # Prepare data for template rendering
        generated_date = datetime.datetime.now().strftime("%B %d, %Y")

        # Transform resume data for template to match frontend preview
        def format_date(date_obj):
            if not date_obj:
                return None
            return date_obj.strftime("%b %Y")

        def transform_resume(resume):
            # Convert ORM to dict and add formatted dates and mapped fields
            r = resume.__dict__.copy()

            # Personal info mapping
            if resume.personal_info:
                pi = resume.personal_info.__dict__.copy()
                pi['linkedin_url'] = pi.get('linkedin')
                pi['github_url'] = pi.get('github')
                pi['portfolio_url'] = pi.get('portfolio')
                r['personal_info'] = pi
            else:
                r['personal_info'] = None

            # Format dates in experience
            if resume.experience:
                exp_list = []
                for exp in resume.experience:
                    e = exp.__dict__.copy()
                    e['start_date_formatted'] = format_date(e.get('start_date'))
                    e['end_date_formatted'] = format_date(e.get('end_date'))
                    exp_list.append(e)
                r['experience'] = exp_list
            else:
                r['experience'] = []

            # Format dates in education
            if resume.education:
                edu_list = []
                for edu in resume.education:
                    ed = edu.__dict__.copy()
                    ed['start_date_formatted'] = format_date(ed.get('start_date'))
                    ed['end_date_formatted'] = format_date(ed.get('end_date'))
                    edu_list.append(ed)
                r['education'] = edu_list
            else:
                r['education'] = []

            # Format skills (map level to proficiency if needed)
            if resume.skills:
                skills_list = []
                for skill in resume.skills:
                    s = skill.__dict__.copy()
                    skills_list.append(s)
                r['skills'] = skills_list
            else:
                r['skills'] = []

            # Format projects (map link to url, format dates)
            if resume.projects:
                proj_list = []
                for proj in resume.projects:
                    p = proj.__dict__.copy()
                    p['url'] = p.get('link')
                    p['start_date_formatted'] = format_date(p.get('start_date'))
                    p['end_date_formatted'] = format_date(p.get('end_date'))
                    proj_list.append(p)
                r['projects'] = proj_list
            else:
                r['projects'] = []

            # Format certifications (format dates)
            if resume.certifications:
                cert_list = []
                for cert in resume.certifications:
                    c = cert.__dict__.copy()
                    c['date_formatted'] = format_date(c.get('date'))
                    cert_list.append(c)
                r['certifications'] = cert_list
            else:
                r['certifications'] = []

            # Format achievements (format dates)
            if resume.achievements:
                ach_list = []
                for ach in resume.achievements:
                    a = ach.__dict__.copy()
                    a['date'] = a.get('date')
                    ach_list.append(a)
                r['achievements'] = ach_list
            else:
                r['achievements'] = []

            # Format extracurriculars (format dates)
            if resume.extracurriculars:
                extra_list = []
                for extra in resume.extracurriculars:
                    ex = extra.__dict__.copy()
                    extra_list.append(ex)
                r['extracurriculars'] = extra_list
            else:
                r['extracurriculars'] = []

            # Format courses (format dates)
            if resume.courses:
                course_list = []
                for course in resume.courses:
                    co = course.__dict__.copy()
                    co['date_completed'] = co.get('date_completed')
                    course_list.append(co)
                r['courses'] = course_list
            else:
                r['courses'] = []

            # Format volunteer work (format dates)
            if resume.volunteer_work:
                vol_list = []
                for vol in resume.volunteer_work:
                    v = vol.__dict__.copy()
                    vol_list.append(v)
                r['volunteer_work'] = vol_list
            else:
                r['volunteer_work'] = []

            # Format publications (format dates)
            if resume.publications:
                pub_list = []
                for pub in resume.publications:
                    p = pub.__dict__.copy()
                    pub_list.append(p)
                r['publications'] = pub_list
            else:
                r['publications'] = []

            return r

        transformed_resume = transform_resume(resume)

        # Render the HTML template with transformed resume data and visible sections
        rendered_html = render_template(
            f"modern.html" if template == "modern" else "default.html",
            resume=transformed_resume,
            visible_sections=visible_sections,
            generated_date=generated_date
        )

        # Generate PDF from rendered HTML using pdfkit
        pdf_bytes = pdfkit.from_string(rendered_html, False)

        # Return PDF as response with CORS headers
        from flask import Response
        response = Response(pdf_bytes, mimetype='application/pdf')
        response.headers['Content-Disposition'] = f'attachment; filename=resume_{resume_id}.pdf'
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
        return response
    except Exception as e:
        current_app.logger.error(f"Error exporting resume {resume_id}: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        response = make_response(jsonify({"error": "Internal server error"}), 500)
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
        return response

@api.route("/test", methods=["GET"])
def test_endpoint():
    return jsonify({"message": "API is working"}), 200

resume_parser = ResumeParser()
resume_optimizer = ResumeOptimizer()
resume_generator = ResumeGenerator()

@api.route("/resumes/<resume_id>/optimize", methods=["POST", "OPTIONS"])
def optimize_resume(resume_id):
    from flask import make_response
    import traceback
    # Handle CORS preflight
    if request.method == "OPTIONS":
        response = make_response('', 204)
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response

    try:
        db = next(get_db())
        resume_obj = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume_obj:
            response = make_response(jsonify({"error": "Resume not found"}), 404)
            response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
            return response

        # Convert resume_obj to dict for optimizer
        from api.schemas import ResumeResponse
        resume_data = ResumeResponse.from_orm(resume_obj).dict()

        # Get job description from request JSON
        job_description = request.json.get("job_description", "")

        # Use ResumeOptimizer service to optimize the resume for the job description
        optimization_result = resume_optimizer.optimize_for_job(resume_data, job_description)

        response = make_response(jsonify(optimization_result), 200)
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
        return response
    except Exception as e:
        current_app.logger.error(f"Error optimizing resume {resume_id}: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        response = make_response(jsonify({"error": "Internal server error"}), 500)
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
        return response

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

@api.route("/resumes/<resume_id>", methods=["GET", "DELETE"])
def get_or_delete_resume(resume_id):
    db = next(get_db())
    if request.method == "GET":
        try:
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
    elif request.method == "DELETE":
        try:
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if not resume:
                return jsonify({"error": "Resume not found"}), 404
            db.delete(resume)
            db.commit()
            return jsonify({"message": "Resume deleted successfully"}), 200
        except Exception as e:
            current_app.logger.error(f"Error deleting resume {resume_id}: {str(e)}")
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
