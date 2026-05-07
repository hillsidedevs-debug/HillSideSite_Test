from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_required
from HillSide.extensions import mail, limiter
from flask_mail import Message
from HillSide.forms.contact_form import ContactForm
from HillSide.forms.captcha_form import CaptchaForm
from HillSide.models import User
from datetime import datetime, timedelta
import time
import os
from flask import send_from_directory, current_app, request

main_bp = Blueprint('main', __name__)


def is_captcha_verified():
    if 'captcha_verified' not in session:
        return False
    
    expiry = session.get('captcha_expiry')
    if expiry is None:
        return False
    
    # Safety net: Convert datetime to timestamp if it's the wrong type
    if isinstance(expiry, datetime):
        expiry = expiry.timestamp()  # Converts datetime to float timestamp
    elif not isinstance(expiry, (int, float)):  # If it's junk, bail
        session.pop('captcha_verified', None)
        session.pop('captcha_expiry', None)
        return False
    
    if time.time() > expiry:  # Now both are floats—safe!
        session.pop('captcha_verified', None)
        session.pop('captcha_expiry', None)
        return False
    
    return True

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')
    
@main_bp.route('/test')
def test():
    return render_template('basic.html')
@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/services')
def services():
    return render_template('services.html')

@main_bp.route('/contact', methods=['GET', 'POST'])
@limiter.limit("5 per hour", methods=["POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # Sanitize name to prevent header injection
        safe_name = "".join(form.name.data.splitlines())
        
        msg = Message(
            subject=f"Contact Form: {safe_name}",
            recipients=['hillside.devs@gmail.com'],
            # Using a safer body format
            body=f"Name: {safe_name}\nEmail: {form.email.data}\n\nMessage:\n{form.message.data}",
            reply_to=form.email.data
        )
        try:
            mail.send(msg)
            flash('✅ Message sent successfully!', 'success')
        except Exception:
            # Avoid printing raw Exception to frontend; log it internally
            # current_app.logger.error(f"Mail failure: {e}") 
            flash('❌ Error sending message. Please try again later.', 'danger')
        
        return redirect(url_for('main.contact'))

    return render_template('contact.html', form=form)

@main_bp.route('/download-resume/<filename>')
@login_required
def download_resume(filename):
    # This points to the absolute path of your root uploads folder
    resume_dir = os.path.join(current_app.root_path, '../uploads/resumes')
    return send_from_directory(resume_dir, filename, as_attachment=True)



@main_bp.route('/upload-error')
def upload_error():
    flash("The file you uploaded exceeds the size limit. Please try a smaller file.", "danger")
    
    # redirect to the page they came from, or home page as a fallback
    target = request.referrer or url_for('main.index')
    return redirect(target)