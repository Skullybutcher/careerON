from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import date, datetime

# User schemas
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

    class Config:
        orm_mode=True
        from_attributes = True

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime

    class Config:
        orm_mode=True        
        from_attributes = True

# Resume section schemas
class PersonalInfoSchema(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True
        arbitrary_types_allowed = True

class EducationSchema(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    gpa: Optional[float] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True
        arbitrary_types_allowed = True

class ExperienceSchema(BaseModel):
    company: str
    position: str
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    current: Optional[bool] = False
    description: Optional[str] = None
    achievements: Optional[List[str]] = []

    class Config:
        orm_mode = True
        from_attributes = True
        arbitrary_types_allowed = True

class SkillSchema(BaseModel):
    name: str
    level: Optional[str] = None
    category: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True
        arbitrary_types_allowed = True

class ProjectSchema(BaseModel):
    title: str
    description: Optional[str] = None
    technologies: Optional[List[str]] = []
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    link: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True
        arbitrary_types_allowed = True

class AchievementSchema(BaseModel):
    title: str
    description: Optional[str] = None
    date: Optional[date] = None
    issuer: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True
        arbitrary_types_allowed = True

class ExtracurricularSchema(BaseModel):
    activity: str
    organization: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True
        arbitrary_types_allowed = True

class CourseSchema(BaseModel):
    name: str
    institution: Optional[str] = None
    date_completed: Optional[date] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class CertificationSchema(BaseModel):
    name: str
    issuer: Optional[str] = None
    date: Optional[date] = None
    credential_id: Optional[str] = None
    url: Optional[str] = None

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class VolunteerWorkSchema(BaseModel):
    organization: str
    role: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class PublicationSchema(BaseModel):
    title: str
    authors: Optional[List[str]] = []
    publication: Optional[str] = None
    date: Optional[date] = None
    url: Optional[str] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class ResumeSectionSchema(BaseModel):
    name: str
    visible: bool = True
    order: int

    class Config:
        orm_mode = True

# Resume schemas
class ResumeCreate(BaseModel):
    title: str
    summary: Optional[str] = None
    section_settings: Optional[List[ResumeSectionSchema]] = []

class ResumeUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    section_settings: Optional[List[ResumeSectionSchema]] = None

class ResumeResponse(BaseModel):
    id: str
    user_id: str
    title: str
    summary: Optional[str] = None
    section_settings: List[ResumeSectionSchema]
    personal_info: Optional[PersonalInfoSchema] = None
    education: List[EducationSchema] = []
    experience: List[ExperienceSchema] = []
    skills: List[SkillSchema] = []
    projects: List[ProjectSchema] = []
    achievements: List[AchievementSchema] = []
    extracurriculars: List[ExtracurricularSchema] = []
    courses: List[CourseSchema] = []
    certifications: List[CertificationSchema] = []
    volunteer_work: List[VolunteerWorkSchema] = []
    publications: List[PublicationSchema] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

# Services schemas
class ResumeOptimizeRequest(BaseModel):
    job_description: str

class ResumeOptimizeResponse(BaseModel):
    score: float
    suggestions: List[str]
    optimized_summary: Optional[str] = None
    keyword_matches: dict

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str = None
