from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash

# Create extension instances HERE (do NOT import from .)
db = SQLAlchemy()
login_manager = LoginManager()


class User(UserMixin, db.Model):
    """User model for both patients and doctors (role: 'patient' or 'doctor')."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'patient' or 'doctor'

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class File(db.Model):
    """Uploaded files linked to a patient (User with role='patient')."""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)          # stored name on disk
    original_filename = db.Column(db.String(255), nullable=False) # original name
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class Prescription(db.Model):
    """Prescription written by a doctor for a patient."""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    """Tell Flask-Login how to load a user from the DB by ID."""
    return User.query.get(int(user_id))
