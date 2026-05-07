from dotenv import load_dotenv
load_dotenv()


from flask import Flask, app, render_template_string
from flask_talisman import Talisman
from werkzeug.middleware.proxy_fix import ProxyFix
from HillSide.extensions import db, mail, bcrypt, login_manager, migrate, csrf, limiter
from HillSide.config import DevelopmentConfig, ProductionConfig, TestingConfig
from HillSide.routes import register_blueprints
from HillSide.models import User
import os
import traceback

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
            "'unsafe-inline'"
        ],
        'script-src': [
            "'self'",
            'https://cdn.jsdelivr.net',
            'https://code.jquery.com',
            'https://www.google.com',
            'https://www.gstatic.com',
            'https://ajax.googleapis.com',      # Maps component library
            'https://maps.googleapis.com',
            "'wasm-unsafe-eval'",
            "'unsafe-inline'"
        ],
        'frame-src': [
            "'self'",
            'https://www.google.com',
            'https://recaptcha.google.com'
        ],
        'font-src': [
            "'self'",
            'https://fonts.gstatic.com',
            'https://www.google.com',
            'https://cdn.jsdelivr.net'
        ],
        'img-src': [
            "'self'",
            'data:',
            'https://cdn-icons-png.flaticon.com',
            'https://maps.googleapis.com',      # Map tiles
            'https://maps.gstatic.com',         # Map icons/markers
            'https://streetviewpixels-pa.googleapis.com',  # Street view
        ],
        'connect-src': [                        # NEW — API calls
            "'self'",
            'https://maps.googleapis.com',
            'https://places.googleapis.com',
        ],
        'worker-src': [                         # NEW — Maps uses web workers
            "'self'",
            'blob:',
        ],
    }

    force_https = (env == "production") and (os.getenv("FORCE_HTTPS", "true").lower() != "false")
    Talisman(
        app,
        content_security_policy=csp,
        force_https=force_https,
    )

    if env == "production":
        app.config.from_object(ProductionConfig)
        app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
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

    @app.errorhandler(500)
    def internal_error(e):
        tb = traceback.format_exc()
        app.logger.error(tb)
        return render_template_string("""
<!doctype html><html><head>
<title>500 – Internal Server Error</title>
<style>
  body { font-family: monospace; background: #1a1a1a; color: #f8f8f2; padding: 2rem; }
  h1 { color: #ff5555; }
  pre { background: #282828; padding: 1.5rem; border-radius: 6px; overflow-x: auto;
        white-space: pre-wrap; word-break: break-word; font-size: 0.85rem; }
</style></head><body>
<h1>500 – Internal Server Error</h1>
<pre>{{ tb }}</pre>
</body></html>""", tb=tb), 500

    return app
