from flask import Blueprint, render_template, redirect, url_for, flash, session
from HillSide.extensions import mail
from flask_mail import Message
from HillSide.forms.contact_form import ContactForm
from HillSide.forms.captcha_form import CaptchaForm
from datetime import datetime, timedelta
import time

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
    # if is_captcha_verified():
    #     return render_template('index.html')
    
    # form = CaptchaForm()
    # if form.validate_on_submit():
    # # Verification is automatic via RecaptchaField
    #     session['captcha_verified'] = True
    #     session['captcha_expiry'] = time.time() + (30 * 60)  # 30 minutes = 1800 seconds
    #     return render_template('index.html')
    
    # return render_template('captcha.html', form=form)
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
def contact():
    form = ContactForm()
    
    if form.validate_on_submit():
        msg = Message(
            subject=f"New Contact Message from {form.name.data}",
            recipients=['hillside.devs@gmail.com'], 
            body=f"""
            You received a new message from your website contact form.

            Name: {form.name.data}
            Email: {form.email.data}

            Message:
            {form.message.data}
            """,
            reply_to=form.email.data 
        )

        try:
            mail.send(msg)
            flash('✅ Your message has been sent successfully! We’ll get back to you soon.', 'success')
        except Exception as e:
            print(e)
            flash('❌ Something went wrong while sending your message. Please try again later.', 'danger')

        return redirect(url_for('main.contact'))
    
    return render_template('contact.html', form=form)