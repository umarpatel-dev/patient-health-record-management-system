from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from .models import db, User

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        
        if current_user.role == "patient":
            return redirect(url_for("views.patient_dashboard"))
        elif current_user.role == "doctor":
            return redirect(url_for("views.doctor_dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully.", "success")

            if user.role == "patient":
                return redirect(url_for("views.patient_dashboard"))
            else:
                return redirect(url_for("views.doctor_dashboard"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html")


@auth.route("/register/patient", methods=["GET", "POST"])
def register_patient():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("Please fill in all fields.", "warning")
        elif password != confirm:
            flash("Passwords do not match.", "warning")
        elif User.query.filter_by(email=email).first():
            flash("Email is already registered.", "warning")
        else:
            user = User(name=name, email=email, role="patient")
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Patient account created. You can now log in.", "success")
            return redirect(url_for("auth.login"))

    return render_template("register_patient.html")


@auth.route("/register/doctor", methods=["GET", "POST"])
def register_doctor():
    # NOTE: in a real system, restrict this route to admins
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("Please fill in all fields.", "warning")
        elif password != confirm:
            flash("Passwords do not match.", "warning")
        elif User.query.filter_by(email=email).first():
            flash("Email is already registered.", "warning")
        else:
            user = User(name=name, email=email, role="doctor")
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Doctor account created. You can now log in.", "success")
            return redirect(url_for("auth.login"))

    return render_template("register_doctor.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
