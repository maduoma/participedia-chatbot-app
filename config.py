# File: config.py

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost/chatbot_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY'
    SERPAPI_API_KEY = 'YOUR_SERPAPI_API_KEY'
    SECRET_KEY = 'secretkey'
