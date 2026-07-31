import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "secret")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///bakery.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    database_url = os.getenv("DATABASE_URL")

    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1,
        )

    SQLALCHEMY_DATABASE_URI = database_url or "sqlite:///bakery.db"