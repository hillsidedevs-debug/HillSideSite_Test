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

from flask import Flask
from HillSide.extensions import db, mail, bcrypt, login_manager, migrate
from HillSide.config import Config
from HillSide.routes import register_blueprints
from HillSide.models import User

def create_app(config_object=None):
    app = Flask(__name__)

    # Load base config
    app.config.from_object(Config)

    # If tests pass in their own config, apply it BEFORE initializing extensions
    if config_object:
        app.config.update(config_object)

    # Now initialize extensions with the final config
    db.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    register_blueprints(app)

    with app.app_context():
        db.create_all()  # Creates all tables defined in models
        print("Database initialized successfully!")

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
