import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = "postgresql://ayush:ayush@localhost:5432/career_navigator"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
