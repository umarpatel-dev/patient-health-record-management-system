import os

from flask import Blueprint, render_template, redirect, url_for, abort, flash, request, current_app, send_from_directory
from flask_login import login_required, current_user

from .models import db, User, File, Prescription

views = Blueprint("views", __name__)


@views.route("/")
def index():
    return render_template("index.html")


# ---------- Patient ----------

@views.route("/patient/dashboard")
@login_required
def patient_dashboard():
    if current_user.role != "patient":
        abort(403)

    files = File.query.filter_by(patient_id=current_user.id).order_by(File.uploaded_at.desc()).all()
    prescriptions = Prescription.query.filter_by(patient_id=current_user.id).order_by(
        Prescription.created_at.desc()
    ).all()

    return render_template(
        "patient_dashboard.html",
        files=files,
        prescriptions=prescriptions,
    )


@views.route("/patient/upload", methods=["GET", "POST"])
@login_required
def patient_upload():
    if current_user.role != "patient":
        abort(403)

    if request.method == "POST":
        uploaded_file = request.files.get("file")

        if not uploaded_file or uploaded_file.filename == "":
            flash("Please select a file to upload.", "warning")
            return redirect(request.url)

        original_name = uploaded_file.filename
        safe_name = f"{current_user.id}_{original_name}"

        upload_folder = current_app.config["UPLOAD_FOLDER"]
        file_path = os.path.join(upload_folder, safe_name)
        uploaded_file.save(file_path)

        record = File(
            patient_id=current_user.id,
            filename=safe_name,
            original_filename=original_name,
        )
        db.session.add(record)
        db.session.commit()

        flash("File uploaded successfully.", "success")
        return redirect(url_for("views.patient_dashboard"))

    return render_template("upload.html")


# ---------- Doctor ----------
@views.route("/doctor/dashboard", methods=["GET", "POST"])
@login_required
def doctor_dashboard():
    if current_user.role != "doctor":
        abort(403)

    search_query = request.args.get("search", "").strip()

    if search_query:
        # Filter by patient name (case-insensitive)
        patients = User.query.filter(
            User.role == "patient",
            User.name.ilike(f"%{search_query}%")
        ).order_by(User.name.asc()).all()
    else:
        patients = User.query.filter_by(role="patient").order_by(User.name.asc()).all()

    return render_template(
        "doctor_dashboard.html",
        patients=patients,
        search_query=search_query,
    )




@views.route("/doctor/patient/<int:patient_id>")
@login_required
def doctor_patient_detail(patient_id):
    if current_user.role != "doctor":
        abort(403)

    patient = User.query.filter_by(id=patient_id, role="patient").first_or_404()
    files = File.query.filter_by(patient_id=patient.id).order_by(File.uploaded_at.desc()).all()
    prescriptions = Prescription.query.filter_by(patient_id=patient.id).order_by(
        Prescription.created_at.desc()
    ).all()

    return render_template(
        "doctor_patient_detail.html",
        patient=patient,
        files=files,
        prescriptions=prescriptions,
    )


@views.route("/doctor/patient/<int:patient_id>/prescribe", methods=["GET", "POST"])
@login_required
def doctor_prescribe(patient_id):
    if current_user.role != "doctor":
        abort(403)

    patient = User.query.filter_by(id=patient_id, role="patient").first_or_404()

    if request.method == "POST":
        text = request.form.get("text", "").strip()
        if not text:
            flash("Prescription text cannot be empty.", "warning")
        else:
            prescription = Prescription(
                patient_id=patient.id,
                doctor_id=current_user.id,
                text=text,
            )
            db.session.add(prescription)
            db.session.commit()
            flash("Prescription saved.", "success")
            return redirect(url_for("views.doctor_patient_detail", patient_id=patient.id))

    return render_template("doctor_prescribe.html", patient=patient)


# ---------- File download ----------

@views.route("/files/<int:file_id>")
@login_required
def download_file(file_id):
    file_record = File.query.get_or_404(file_id)

    if current_user.role == "patient":
        if file_record.patient_id != current_user.id:
            abort(403)
    elif current_user.role != "doctor":
        abort(403)

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    return send_from_directory(
        upload_folder,
        file_record.filename,
        as_attachment=True,
        download_name=file_record.original_filename,
    )
