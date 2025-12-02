import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'replace-this-with-a-secure-random-string')
    RECAPTCHA_PUBLIC_KEY = '6LfkAAosAAAAAGD7cINGSpI9Zl8V_RiNKaBozPOK'
    RECAPTCHA_PRIVATE_KEY = '6LfkAAosAAAAAIt6TAkkJbzbYzjHaDBKHmn289mA'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///users.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # MAIL_SERVER = 'smtp.gmail.com'
    # MAIL_PORT = 587
    # MAIL_USE_TLS = True
    # MAIL_USERNAME = 'hillside.devs@gmail.com'
    # MAIL_PASSWORD = 'tvsj fhfm wazs ybdi '
    
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 8025
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None

    
    MAIL_DEFAULT_SENDER = ('Your Website', 'hillside.devs@gmail.com')