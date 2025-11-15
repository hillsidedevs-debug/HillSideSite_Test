from flask_wtf import FlaskForm
from wtforms import SubmitField
from flask_wtf.recaptcha import RecaptchaField

class CaptchaForm(FlaskForm):
    recaptcha = RecaptchaField()
    submit = SubmitField('Verify I\'m Human')