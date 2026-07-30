import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///bakery.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

   
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///bakery.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # M-Pesa Config
    MPESA_CONSUMER_KEY = os.getenv('CONSUMER_KEY')
    MPESA_CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
    MPESA_BUSINESS_SHORTCODE = os.getenv('BUSINESS_SHORTCODE', '174379')
    MPESA_PASSKEY = os.getenv('PASSKEY')
    MPESA_CALLBACK_URL = os.getenv('CALLBACK_URL')
    MPESA_BASE_URL = os.getenv('MPESA_BASE_URL', 'https://sandbox.safaricom.co.ke')
    
    @classmethod
    def validate_mpesa(cls):
        required = [
            cls.MPESA_CONSUMER_KEY,
            cls.MPESA_CONSUMER_SECRET,
            cls.MPESA_PASSKEY,
            cls.MPESA_CALLBACK_URL
        ]
        missing = [i for i, v in enumerate(required) if not v]
        if missing:
            raise ValueError("Missing required M-Pesa configuration in .env file")