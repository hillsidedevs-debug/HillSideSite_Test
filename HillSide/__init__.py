# from flask import Flask
# from HillSide.extensions import db, mail, bcrypt, login_manager, migrate
# from HillSide.config import Config
# from HillSide.routes import register_blueprints
# from HillSide.models import User


# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)



#     db.init_app(app)
#     mail.init_app(app)
#     bcrypt.init_app(app)
#     login_manager.init_app(app)
#     migrate.init_app(app, db)

#     register_blueprints(app)

#     with app.app_context():
#         db.create_all()  # Creates all tables defined in models
#         print("Database initialized successfully!")

#     @login_manager.user_loader
#     def load_user(user_id):
#         return User.query.get(int(user_id))

#     return app
from dotenv import load_dotenv
load_dotenv()


from flask import Flask, app
from flask_talisman import Talisman
from HillSide.extensions import db, mail, bcrypt, login_manager, migrate, csrf, limiter
from HillSide.config import DevelopmentConfig, ProductionConfig, TestingConfig
from HillSide.routes import register_blueprints
from HillSide.models import User
import os

def create_app(config_object=None):
    app = Flask(__name__)

    # ---- filesystem paths (MUST be set on app.config) ----
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))        # HillSide/
    PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))  # project root

    app.config["BASE_DIR"] = BASE_DIR
    app.config["PROJECT_ROOT"] = PROJECT_ROOT

    app.config["UPLOAD_FOLDER"] = os.path.join(PROJECT_ROOT, "uploads")
    app.config["UPLOAD_PHOTO_FOLDER"] = os.path.join(app.config["UPLOAD_FOLDER"], "photos")
    app.config["UPLOAD_RESUME_FOLDER"] = os.path.join(app.config["UPLOAD_FOLDER"], "resumes")


    env = os.getenv("FLASK_ENV", "development")

    csp = {
        'default-src': "'self'",
        'style-src': [
            "'self'",
            'https://cdn.jsdelivr.net',
            'https://fonts.googleapis.com',
            "'unsafe-inline'"  # Required for many Bootstrap components and Flask-WTF error styling
        ],
        'script-src': [
            "'self'",
            'https://cdn.jsdelivr.net',
            'https://code.jquery.com', # Add this if you use jQuery
            "'unsafe-inline'"          # Use with caution; allows inline <script> tags
        ],
        'font-src': [
            "'self'",
            'https://fonts.gstatic.com'
        ],
        'img-src': ["'self'", 'data:'] # 'data:' allows base64 encoded images
    }

    # Initialize Talisman
    # force_https=False in dev ensures you don't get redirect loops on localhost
    Talisman(
        app, 
        content_security_policy=csp,
        force_https=(True)
    )

    if env == "production":
        app.config.from_object(ProductionConfig)
        # Force HTTPS and set strict CSP
        #Talisman(app, force_https=True)
        print("Running in Production mode")
    elif env == "development":
        app.config.from_object(DevelopmentConfig)
        # Disable HTTPS requirement for local dev
        #Talisman(app, force_https=False)
        print("Running in Development mode")
    elif env == "testing":
        app.config.from_object(TestingConfig)
        print("RRunning in Testing mode")

    else:
        raise RuntimeError(f"Unknown FLASK_ENV: {env}")


    if config_object:
        app.config.update(config_object)

    # Now initialize extensions with the final config
    db.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    limiter.init_app(app)


    register_blueprints(app)

    if not app.config.get("TESTING"):
            with app.app_context():
                db.create_all() # Creates all tables defined in models
                print("Database initialized successfully!")
    else:
        print("Testing mode: Skipping DB initialization")

    print("UPLOAD_PHOTO_FOLDER =", app.config["UPLOAD_PHOTO_FOLDER"])

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
