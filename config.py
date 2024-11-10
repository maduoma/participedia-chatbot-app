# File: config.py

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
