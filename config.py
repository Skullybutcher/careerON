import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = "postgresql://zayed:zayed@localhost:5432/career_navigator"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    HF_TOKEN= os.environ.get("HF_TOKEN")
    DEVICE = os.environ.get("DEVICE", "cpu")  # force CPU usage for low resource machines

    NVIDIA_API_URL = os.environ.get("NVIDIA_API_URL", "https://integrate.api.nvidia.com/v1/chat/completions")
    NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "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")