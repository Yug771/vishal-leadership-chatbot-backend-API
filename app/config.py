import os
from datetime import timedelta

class Config:
    """Base config."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # LlamaCloudIndex configuration
    LLAMA_CLOUD_API_KEY = os.getenv('LLAMA_CLOUD_API_KEY', '')
    LLAMA_CLOUD_INDEX_NAME = os.getenv('LLAMA_CLOUD_INDEX_NAME', 'leadership-chatbot')
    LLAMA_CLOUD_PROJECT_NAME = os.getenv('LLAMA_CLOUD_PROJECT_NAME', 'Default')
    LLAMA_CLOUD_ORGANIZATION_ID = os.getenv('LLAMA_CLOUD_ORGANIZATION_ID', '')
    
    # Swagger configuration
    SWAGGER = {
        "title": "Leadership Chatbot API",
        "description": "API for the Leadership Chatbot application",
        "version": "1.0.0",
        "termsOfService": "",
        "uiversion": 3,
        "specs_route": "/docs/",
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
            }
        },
        "security": [{"Bearer": []}]
    }

class DevelopmentConfig(Config):
    """Development config."""
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///leadership_chatbot_dev.db')

class TestingConfig(Config):
    """Testing config."""
    FLASK_ENV = 'testing'
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', 'sqlite:///leadership_chatbot_test.db')

class ProductionConfig(Config):
    """Production config."""
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY')  # Must be set in production
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')  # Must be set in production
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///leadership_chatbot_prod.db')
    
    # These can be overridden by environment variables
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.getenv('JWT_ACCESS_EXPIRE_MINUTES', 30)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv('JWT_REFRESH_EXPIRE_DAYS', 7))) 