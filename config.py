import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    HF_TOKEN= os.environ.get("HF_TOKEN")
    DEVICE = os.environ.get("DEVICE", "cpu")  # force CPU usage for low resource machines

    NVIDIA_API_URL = os.environ.get("NVIDIA_API_URL", "https://integrate.api.nvidia.com/v1/chat/completions")
    NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY")