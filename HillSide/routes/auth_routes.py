from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from HillSide.forms.register_form import RegisterForm
from HillSide.forms.login_form import LoginForm
from HillSide.extensions import db, bcrypt
from HillSide.models import User, Enrollment
import os
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():

        # Hash password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

        # Create user object
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            phone_number=form.phone_number.data,
            address=form.address.data,
            gender=form.gender.data if form.gender.data else None,
            education_qualification=form.education_qualification.data,
        )

        # Handle profile photo upload
        if form.photo.data:
            photo_filename = secure_filename(form.photo.data.filename)
            form.photo.data.save(os.path.join("static/uploads/photos", photo_filename))
            user.photo = photo_filename

        # Handle resume upload
        if form.resume.data:
            resume_filename = secure_filename(form.resume.data.filename)
            form.resume.data.save(os.path.join("static/uploads/resumes", resume_filename))
            user.resume = resume_filename

        # Save user to DB
        try:
            db.session.add(user)
            db.session.commit()
            flash("Registration successful!", "success")
            return redirect(url_for('main.index'))

        except IntegrityError as e:
            db.session.rollback()

            # Detect which field caused the unique error
            if "email" in str(e.orig):
                flash("Email already exists. Please use a different one.", "danger")
            elif "username" in str(e.orig):
                flash("Username already exists. Please choose a different one.", "danger")
            else:
                flash("A database error occurred. Please try again.", "danger")

    return render_template("register.html", form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    print(form.errors)
    print(request.method)
    print(form.data)

    print("outside")
    if form.validate_on_submit():
        print("validated")

        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password', 'danger')
    else:
        print("validation failed", form.errors)
    
    return render_template('login.html', form=form)

@auth_bp.route("/dashboard")
@login_required
def dashboard():
    enrollments = Enrollment.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', enrollments=enrollments)

@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))