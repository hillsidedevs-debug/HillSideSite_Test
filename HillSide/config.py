import os


# class Config:
#     SECRET_KEY = os.getenv('SECRET_KEY', 'replace-this-with-a-secure-random-string')
#     RECAPTCHA_PUBLIC_KEY = '6LfkAAosAAAAAGD7cINGSpI9Zl8V_RiNKaBozPOK'
#     RECAPTCHA_PRIVATE_KEY = '6LfkAAosAAAAAIt6TAkkJbzbYzjHaDBKHmn289mA'
#     SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///users.db')
#     SQLALCHEMY_TRACK_MODIFICATIONS = False

#     # MAIL_SERVER = 'smtp.gmail.com'
#     # MAIL_PORT = 587
#     # MAIL_USE_TLS = True
#     # MAIL_USERNAME = 'hillside.devs@gmail.com'
#     # MAIL_PASSWORD = 'tvsj fhfm wazs ybdi '
    
#     MAIL_SERVER = 'localhost'
#     MAIL_PORT = 8025
#     MAIL_USE_TLS = False
#     MAIL_USE_SSL = False
#     MAIL_USERNAME = None
#     MAIL_PASSWORD = None

    
#     MAIL_DEFAULT_SENDER = ('Your Website', 'hillside.devs@gmail.com')


import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY is not set")
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///users.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # reCAPTCHA config
    RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY')

    # default sender
    MAIL_DEFAULT_SENDER = (
        os.getenv("MAIL_SENDER_NAME"),
        os.getenv("MAIL_SENDER_EMAIL")
    )
    if not MAIL_DEFAULT_SENDER[0]:
        raise RuntimeError("MAIL_SENDER_NAME is not set")
    if not MAIL_DEFAULT_SENDER[1]:
        raise RuntimeError("MAIL_SENDER_EMAIL is not set")


class DevelopmentConfig(Config):
    DEBUG = True

    # Use local mail server (MailHog, MailPit, Python smtpd, etc.)
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 8025
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None


class ProductionConfig(Config):
    DEBUG = False

    # Use real Gmail SMTP
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    if not MAIL_USERNAME:
        raise RuntimeError("MAIL_USERNAME is not set")
    if not MAIL_PASSWORD:
        raise RuntimeError("MAIL_PASSWORD is not set")
