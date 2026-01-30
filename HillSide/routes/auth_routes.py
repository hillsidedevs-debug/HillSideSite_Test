from flask import (
    Blueprint, render_template, redirect,
    url_for, flash, request, current_app
)
from flask_login import (
    login_user, logout_user,
    login_required, current_user
)
from sqlalchemy.exc import IntegrityError
from itsdangerous import URLSafeTimedSerializer
import os

from HillSide.forms.register_form import RegisterForm
from HillSide.forms.login_form import LoginForm
from HillSide.forms.forgot_password_form import ForgotPasswordForm
from HillSide.forms.reset_password_form import ResetPasswordForm
from HillSide.forms.update_profile_form import UpdateProfileForm

from HillSide.extensions import db, bcrypt, limiter
from HillSide.models import User, Enrollment
from HillSide.utils import (
    send_reset_email,
    send_verification_email,
    generate_secure_filename,
    is_valid_file
)
from HillSide.models import GenderEnum
from flask import session 

auth_bp = Blueprint("auth", __name__)


# --------------------
# Helpers
# --------------------

def get_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


# --------------------
# Register
# --------------------

@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("3 per minute")
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        # 1. PRE-VALIDATE FILES (Strict MIME checking)
        if form.photo.data:
            if not is_valid_file(form.photo.data, 'image'):
                flash("Invalid image. Only JPG and PNG are allowed.", "danger")
                return render_template("register.html", form=form)

        if form.resume.data:
            if not is_valid_file(form.resume.data, 'pdf'):
                flash("Invalid resume. Only PDF files are allowed.", "danger")
                return render_template("register.html", form=form)

        # 2. HASH PASSWORD
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

        # 3. INITIALIZE USER OBJECT
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            phone_number=form.phone_number.data,
            address=form.address.data,
            gender=form.gender.data or None,
            education_qualification=form.education_qualification.data,
            is_verified=False,
        )

        try:
            # 4. DATABASE SYNC & FILE SAVING
            db.session.add(user)
            # Use flush() to check for IntegrityErrors (duplicate email/user) 
            # before writing files to the disk
            db.session.flush()

            # Handle Photo
            if form.photo.data:
                filename = generate_secure_filename("photo", "jpg")
                path = os.path.join(current_app.config["UPLOAD_FOLDER"], "photos", filename)
                form.photo.data.save(path)
                user.photo = filename

            # Handle Resume
            if form.resume.data:
                filename = generate_secure_filename("resume", "pdf")
                path = os.path.join(current_app.config["UPLOAD_FOLDER"], "resumes", filename)
                form.resume.data.save(path)
                user.resume = filename

            # Final Commit
            db.session.commit()

            # 5. POST-REGISTRATION LOGIC
            if current_app.config.get("TESTING"):
                user.is_verified = True
                db.session.commit()
            else:
                send_verification_email(user)

            flash("Registration successful. Please verify your email.", "info")
            return redirect(url_for("auth.login"))

        except IntegrityError:
            db.session.rollback()
            flash("Email or username already exists.", "danger")

    return render_template("register.html", form=form)


# --------------------
# Login
# --------------------

@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if not user or not bcrypt.check_password_hash(
            user.password, form.password.data
        ):
            flash("Invalid email or password.", "danger")
            return render_template("login.html", form=form)

        if not user.is_verified:
            flash("Please verify your email before logging in.", "warning")
            return render_template(
                "login.html", form=form,
                show_resend=True, email=user.email
            )

        # SECURITY: Protect against Session Fixation
        session.clear() # Wipe the old session
        session.permanent = True # Enforce the lifetime set in config.py
        
        login_user(user)
        return redirect(url_for("main.index"))

    return render_template("login.html", form=form)


# --------------------
# Dashboard
# --------------------

@auth_bp.route("/dashboard")
@login_required
def dashboard():
    enrollments = Enrollment.query.filter_by(
        user_id=current_user.id
    ).all()
    return render_template("dashboard.html", enrollments=enrollments, GenderEnum=GenderEnum)


# --------------------
# Logout
# --------------------

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


# --------------------
# Update Profile
# --------------------

@auth_bp.route("/profile", methods=["POST"])
@limiter.limit("5 per minute")
@login_required
def update_profile():
    form = UpdateProfileForm()
    
    # We validate but skip the password re-auth per your request
    if not form.validate_on_submit():
        flash("Invalid input. Please correct the errors.", "danger")
        return redirect(url_for("auth.dashboard"))

    # Update basic fields
    current_user.first_name = form.first_name.data
    current_user.last_name = form.last_name.data
    current_user.phone_number = form.phone_number.data
    current_user.gender = form.gender.data or None
    current_user.education_qualification = form.education_qualification.data
    current_user.address = form.address.data

    # Email/Username change logic
    if form.username.data != current_user.username:
        current_user.username = form.username.data

    if form.email.data != current_user.email:
        current_user.email = form.email.data
        current_user.is_verified = False
        send_verification_email(current_user)
        flash("Email changed. Please verify your new email.", "warning")

    # 1. FILE CLEANUP & UPDATE LOGIC
    # We iterate through photo and resume to keep the code DRY (Don't Repeat Yourself)
    file_configs = [
        ('photo', 'photos', 'image', 'jpg'),
        ('resume', 'resumes', 'pdf', 'pdf')
    ]

    for field_name, folder_name, mime_group, extension in file_configs:
        file_data = getattr(form, field_name).data
        
        if file_data:
            # Validate magic bytes
            if not is_valid_file(file_data, mime_group):
                flash(f"Invalid {field_name} file format.", "danger")
                continue

            # DELETE OLD FILE FROM DISK
            old_filename = getattr(current_user, field_name)
            if old_filename:
                old_path = os.path.join(current_app.config["UPLOAD_FOLDER"], folder_name, old_filename)
                try:
                    if os.path.exists(old_path):
                        os.remove(old_path)
                except Exception as e:
                    # Log error but don't stop the process
                    print(f"Error deleting old {field_name}: {e}")

            # SAVE NEW FILE
            new_filename = generate_secure_filename(field_name, extension)
            new_path = os.path.join(current_app.config["UPLOAD_FOLDER"], folder_name, new_filename)
            file_data.save(new_path)
            
            # Update database record
            setattr(current_user, field_name, new_filename)

    try:
        db.session.commit()
        flash("Profile updated successfully.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Username or email already exists.", "danger")

    return redirect(url_for("auth.dashboard"))


# --------------------
# Forgot Password
# --------------------

@auth_bp.route("/forgot_password", methods=["GET", "POST"])
@limiter.limit("3 per minute")
def forgot_password():
    print("in forgot_password")
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)

        flash("If the email exists, a reset link has been sent.", "info")
        return redirect(url_for("auth.login"))

    return render_template("forgot_password.html", form=form)


# --------------------
# Reset Password
# --------------------

@auth_bp.route("/reset_password/<token>", methods=["GET", "POST"])
@limiter.limit("10 per hour")
def reset_password(token):
    user = User.verify_reset_token(token)

    if not user:
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for("auth.forgot_password"))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        user.password = bcrypt.generate_password_hash(
            form.password.data
        ).decode("utf-8")
        db.session.commit()

        flash("Your password has been updated.", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", form=form)


# --------------------
# Verify Email
# --------------------

@auth_bp.route("/verify/<token>")
@limiter.limit("10 per hour")
def verify_email(token):
    try:
        email = get_serializer().loads(
            token, salt="email-verify", max_age=3600
        )
    except Exception:
        flash("Invalid or expired verification link.", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("auth.login"))

    if user.is_verified:
        flash("Account already verified.", "info")
        return redirect(url_for("auth.login"))

    user.is_verified = True
    db.session.commit()

    flash("Email verified successfully.", "success")
    return redirect(url_for("auth.login"))


# --------------------
# Resend Verification
# --------------------

@auth_bp.route("/resend-verification", methods=["POST"])
@limiter.limit("3 per minute")
def resend_verification():
    email = request.form.get("email")

    if not email:
        flash("Invalid request.", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=email).first()

    if user and not user.is_verified:
        send_verification_email(user)

    flash("If applicable, a verification email has been sent.", "info")
    return redirect(url_for("auth.login"))
