from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email
from flask_wtf.recaptcha import RecaptchaField  # <-- Add this import

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])
    # recaptcha = RecaptchaField()  # <-- Adds the reCAPTCHA widget
    submit = SubmitField('Send Message')

