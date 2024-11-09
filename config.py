# File: config.py

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost/chatbot_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENAI_API_KEY = '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'
    SERPAPI_API_KEY = 'afc6be8414f2de36ebc94e1a3a37862b1f7adfd1b67bfe0935dffbb774b9b050'
    SECRET_KEY = 'secretkey'
