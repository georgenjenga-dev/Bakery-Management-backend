import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:

    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///bakery.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "jwt-secret-key"
    )

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    MPESA_CONSUMER_KEY = os.getenv("CONSUMER_KEY")
    MPESA_CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
    MPESA_BUSINESS_SHORTCODE = os.getenv(
        "BUSINESS_SHORTCODE",
        "174379"
    )
    MPESA_PASSKEY = os.getenv("PASSKEY")
    MPESA_CALLBACK_URL = os.getenv("CALLBACK_URL")
    MPESA_BASE_URL = os.getenv(
        "MPESA_BASE_URL",
        "https://sandbox.safaricom.co.ke"
    )