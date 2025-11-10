from flask import Blueprint, render_template, redirect, url_for, flash
from HillSide.extensions import mail
from flask_mail import Message
from HillSide.forms.contact_form import ContactForm

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

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