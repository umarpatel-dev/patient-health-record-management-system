import os

from flask import Flask

from .models import db, login_manager  # just import the extension instances


def create_app():
    app = Flask(__name__)

    # ---- Basic configuration ----
    app.config["SECRET_KEY"] = "dev-test-key"  # change later
    basedir = os.path.dirname(os.path.abspath(__file__))

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        basedir, "patient_health_record.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Upload folder
    upload_folder = os.path.join(basedir, "uploads")
    os.makedirs(upload_folder, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = upload_folder
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB

    # ---- Init extensions ----
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # ---- Register blueprints ----
    from .auth import auth
    from .views import views
    app.register_blueprint(auth)
    app.register_blueprint(views)

    # ---- Create tables (dev only) ----
    with app.app_context():
        from .models import User, File, Prescription  # import models AFTER db.init_app
        db.create_all()

    return app
