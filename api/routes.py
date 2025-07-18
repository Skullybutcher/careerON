from flask import Blueprint, request, jsonify, current_app
from flask_cors import CORS
from api.limiter import limiter
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt as pyjwt
from services.resume_parser import ResumeParser
from services.resume_optimizer import ResumeOptimizer
from sqlalchemy.orm import Session
from database.db import get_db
import re
from services.resume_optimizer import ResumeOptimizer

import traceback
from werkzeug.utils import secure_filename
from flask import make_response
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
from api.job_recommendation import llm_recommend_jobs
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


from services.resume_exporter import ResumeExporter

@api.route("/resumes/<resume_id>/export-ats", methods=["GET", "OPTIONS"])
def export_resume_ats(resume_id):
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

        if export_format != "pdf":
            response = make_response(jsonify({"error": "Unsupported export format"}), 400)
            response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
            return response

        db = next(get_db())
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            response = make_response(jsonify({"error": "Resume not found"}), 404)
            response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
            return response

        # Transform resume data for template to match frontend preview
        def format_date(date_obj):
            if not date_obj:
                return None
            return date_obj.strftime("%b %Y")

        def transform_resume(resume):
            r = resume.__dict__.copy()

            if resume.personal_info:
                pi = resume.personal_info.__dict__.copy()
                pi['linkedin_url'] = pi.get('linkedin')
                pi['github_url'] = pi.get('github')
                pi['portfolio_url'] = pi.get('portfolio')
                r['personal_info'] = pi
            else:
                r['personal_info'] = None

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

            if resume.skills:
                skills_list = []
                for skill in resume.skills:
                    s = skill.__dict__.copy()
                    skills_list.append(s)
                r['skills'] = skills_list
            else:
                r['skills'] = []

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

            if resume.certifications:
                cert_list = []
                for cert in resume.certifications:
                    c = cert.__dict__.copy()
                    c['date_formatted'] = format_date(c.get('date'))
                    cert_list.append(c)
                r['certifications'] = cert_list
            else:
                r['certifications'] = []

            if resume.achievements:
                ach_list = []
                for ach in resume.achievements:
                    a = ach.__dict__.copy()
                    a['date'] = a.get('date')
                    ach_list.append(a)
                r['achievements'] = ach_list
            else:
                r['achievements'] = []

            if resume.extracurriculars:
                extra_list = []
                for extra in resume.extracurriculars:
                    ex = extra.__dict__.copy()
                    extra_list.append(ex)
                r['extracurriculars'] = extra_list
            else:
                r['extracurriculars'] = []

            if resume.courses:
                course_list = []
                for course in resume.courses:
                    co = course.__dict__.copy()
                    co['date_completed'] = co.get('date_completed')
                    course_list.append(co)
                r['courses'] = course_list
            else:
                r['courses'] = []

            if resume.volunteer_work:
                vol_list = []
                for vol in resume.volunteer_work:
                    v = vol.__dict__.copy()
                    vol_list.append(v)
                r['volunteer_work'] = vol_list
            else:
                r['volunteer_work'] = []

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

        exporter = ResumeExporter(ats_mode=True)
        pdf_bytes = exporter.export_resume_pdf(transformed_resume)

        from flask import Response
        response = Response(pdf_bytes, mimetype='application/pdf')
        response.headers['Content-Disposition'] = f'attachment; filename=resume_{resume_id}_ats.pdf'
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
        return response
    except Exception as e:
        current_app.logger.error(f"Error exporting ATS resume {resume_id}: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        response = make_response(jsonify({"error": "Internal server error"}), 500)
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
        return response


optimizer = ResumeOptimizer()

# @api.route('/api/apply-resume-changes', methods=['POST'])
# def apply_resume_changes():
#     try:
#         data = request.get_json()
#         resume = data.get('resume')
#         ats_result = data.get('ats_result')  # Must include `issues`
#         keyword_matches = data.get('keyword_matches')  # Dict of keywords and scores

#         if not (resume and ats_result and keyword_matches):
#             return jsonify({"error": "Missing required fields"}), 400

#         # Enhance the resume using Hugging Face-powered rewriting
#         enhanced_resume = optimizer.enhance_resume(resume, ats_result, keyword_matches)

#         return jsonify({
#             "success": True,
#             "message": "Resume enhanced successfully.",
#             "enhanced_resume": enhanced_resume
#         }), 200

#     except Exception as e:
#         return jsonify({
#             "success": False,
#             "message": f"Error enhancing resume: {str(e)}"
#         }), 500
    
@api.route('/resumes/parse', methods=['POST'])
def parse_resume_pdf():
    if 'resume_file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    pdf_file = request.files['resume_file']
    pdf_file.stream.seek(0)

    if pdf_file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    try:
        parser = ResumeParser()
        parsed_data = parser.parse_from_pdf(pdf_file)

        # Create resume object here with parsed summary
        db = next(get_db())

        new_resume = Resume(
            id=str(uuid.uuid4()),
            title="Parsed Resume",
            user_id=None,  # Assign if available
            summary=parsed_data.get("summary", ""),
            section_settings=[
                {"name": "personal_info", "visible": True, "order": 1},
                {"name": "summary", "visible": True, "order": 2},
                {"name": "education", "visible": True, "order": 3},
                {"name": "experience", "visible": True, "order": 4},
                {"name": "skills", "visible": True, "order": 5},
                {"name": "projects", "visible": True, "order": 6},
            ]
        )
        db.add(new_resume)
        db.commit()
        db.refresh(new_resume)

        return jsonify({
            "resume_id": new_resume.id,
            **parsed_data
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

       
    


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

@api.route("/test", methods=["GET"])
def test_endpoint():
    return jsonify({"message": "API is working"}), 200

resume_parser = ResumeParser()
resume_optimizer = ResumeOptimizer()
resume_generator = ResumeGenerator()

@api.route("/resumes/<resume_id>/optimize", methods=["POST", "OPTIONS"])
def optimize_resume(resume_id):
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

        resume_data = ResumeResponse.from_orm(resume_obj).dict()
        job_description = request.json.get("job_description", "")

        # Optimization: similarity, suggestions, skill gap
        optimization_result = resume_optimizer.optimize_for_job(resume_data, job_description)

        # Advanced improvement suggestions
        ats_result = resume_optimizer.check_ats_compatibility(resume_data)
        keyword_matches = {skill: 1.0 if skill not in optimization_result["missing_skills"] else 0.0
                           for skill in optimization_result["missing_skills"]}

        # Call Hugging Face Mistral for feedback (not direct editing)
        improvement_advice = resume_optimizer.enhance_resume(
            resume_data,
            ats_result,
            keyword_matches
        )

        response_data = {
            "optimization": optimization_result,
            "improvement_advice": improvement_advice
        }

        response = make_response(jsonify(response_data), 200)
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
    encoded_jwt = pyjwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
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
            return jsonify(personal_info.__dict__), 200
        except Exception as e:
            current_app.logger.error(f"Error fetching personal info for resume {resume_id}: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    elif request.method == "PUT":
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400

                
            print("Received personal info:", data)

            # Clean or remove invalid email if present

            email = data.get("email")
            if email == "":
                data["email"] = None
            elif email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                current_app.logger.warning(f"Invalid email detected: {email}")
                data["email"] = None  # or optionally: del data["email"]

            # Now validate cleaned data
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
            if not resume:
                return jsonify({"error": "Resume not found"}), 404
            
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
    from datetime import datetime
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
                # Convert empty or invalid date strings to None
                if 'start_date' in exp_data:
                    if not exp_data['start_date']:
                        exp_data['start_date'] = None
                    else:
                        try:
                            exp_data['start_date'] = datetime.strptime(exp_data['start_date'], '%Y-%m-%d').date()
                        except Exception:
                            exp_data['start_date'] = None
                if 'end_date' in exp_data:
                    if not exp_data['end_date']:
                        exp_data['end_date'] = None
                    else:
                        try:
                            exp_data['end_date'] = datetime.strptime(exp_data['end_date'], '%Y-%m-%d').date()
                        except Exception:
                            exp_data['end_date'] = None
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



from flask_cors import cross_origin

# Remove job_rec_bp routes to avoid duplicate route registration

from api.job_recommendation import llm_recommend_jobs, bp as job_rec_bp, get_recommended_jobs, run_scraper

from flask import make_response
from flask_cors import cross_origin

# Instead of registering job_rec_bp blueprint, register its routes directly on api blueprint

@api.route("/recommend", methods=["OPTIONS"])
@cross_origin(origin='http://localhost:8080', headers=['Content-Type', 'Authorization'])
def recommend_options():
    response = make_response('', 204)
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@api.route("/recommend", methods=["POST"])
@cross_origin(origin='http://localhost:8080', headers=['Content-Type', 'Authorization'])
def recommend_post():
    return llm_recommend_jobs()

@api.route("/recommended_jobs.json", methods=["GET"])
def recommended_jobs_json():
    return get_recommended_jobs()

@api.route("/run-scraper", methods=["POST"])
def run_scraper_route():
    return run_scraper()
