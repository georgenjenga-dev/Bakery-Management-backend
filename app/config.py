import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

# -------------------------------------------------------------------
# Database Configuration
# -------------------------------------------------------------------

database_url = os.getenv("DATABASE_URL")

# Render/Heroku compatibility
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://",
        "postgresql://",
        1,
    )


class Config:
    # ----------------------------------------------------------------
    # Flask Configuration
    # ----------------------------------------------------------------
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "dev-secret-key"
    )

    # ----------------------------------------------------------------
    # Database Configuration
    # ----------------------------------------------------------------
    SQLALCHEMY_DATABASE_URI = (
        database_url or "sqlite:///bakery.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ----------------------------------------------------------------
    # JWT Configuration
    # ----------------------------------------------------------------
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "jwt-secret-key"
    )

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # ----------------------------------------------------------------
    # M-Pesa Configuration
    # ----------------------------------------------------------------
    MPESA_CONSUMER_KEY = os.getenv("CONSUMER_KEY")

    MPESA_CONSUMER_SECRET = os.getenv(
        "CONSUMER_SECRET"
    )

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

    # ----------------------------------------------------------------
    # M-Pesa Validation
    # ----------------------------------------------------------------
    @classmethod
    def validate_mpesa(cls):
        required = {
            "CONSUMER_KEY": cls.MPESA_CONSUMER_KEY,
            "CONSUMER_SECRET": cls.MPESA_CONSUMER_SECRET,
            "PASSKEY": cls.MPESA_PASSKEY,
            "CALLBACK_URL": cls.MPESA_CALLBACK_URL,
        }

        missing = [
            key
            for key, value in required.items()
            if not value
        ]

        if missing:
            raise ValueError(
                "Missing required M-Pesa environment variables: "
                + ", ".join(missing)
            )