import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY is not set")

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///users.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ALLOWED_PHOTO_EXTENSIONS = {"jpg", "jpeg", "png"}
    ALLOWED_RESUME_EXTENSIONS = {"pdf"}

    RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY')

    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)

    MAIL_DEFAULT_SENDER = (
        os.getenv("MAIL_SENDER_NAME", "Hillside"),
        os.getenv("MAIL_SENDER_EMAIL", "noreply@example.com"),
    )


class DevelopmentConfig(Config):
    """Local development — real Gmail SMTP so you can see emails end-to-end."""
    DEBUG = True
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")


class TestingConfig(Config):
    """Automated tests (pytest) — no real emails, in-memory DB, CSRF off."""
    TESTING = True
    DEBUG = True
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200 MB

    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    MAIL_SERVER = 'localhost'
    MAIL_PORT = 8025
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None


class ProductionConfig(Config):
    """Production server — strict security, real Gmail SMTP required."""
    DEBUG = False
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200 MB
    RATELIMIT_STORAGE_URI = "redis://localhost:6379"

    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    if not MAIL_USERNAME:
        raise RuntimeError("MAIL_USERNAME is not set")
    if not MAIL_PASSWORD:
        raise RuntimeError("MAIL_PASSWORD is not set")
