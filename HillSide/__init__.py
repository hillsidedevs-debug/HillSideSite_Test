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


from flask import Flask
from HillSide.extensions import db, mail, bcrypt, login_manager, migrate, csrf, limiter
from HillSide.config import DevelopmentConfig, ProductionConfig
from HillSide.routes import register_blueprints
from HillSide.models import User
import os

def create_app(config_object=None):
    app = Flask(__name__)

    env = os.getenv("FLASK_ENV", "development")

    if env == "production":
        app.config.from_object(ProductionConfig)
    elif env == "development":
        app.config.from_object(DevelopmentConfig)
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

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
