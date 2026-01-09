from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SubmitField, PasswordField,
    SelectField
)
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Email, Optional, EqualTo, Length
from HillSide.models import GenderEnum  # import your enum


class RegisterForm(FlaskForm):
    # Added Length constraints to match DB schema
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=100)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=100)])

    username = StringField("Username", validators=[DataRequired(), Length(min=4, max=150)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=150)])
    
    # Enforce a minimum password length for better security
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=128)])
    password_confirm = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')]
    )
    
    phone_number = StringField("Phone Number", validators=[Optional(), Length(max=20)])

    photo = FileField(
        "Profile Photo",
        validators=[Optional(), FileAllowed(["jpg", "jpeg", "png"], "Images only!")]
    )

    # Standardized to PDF to match your backend logic
    resume = FileField(
        "Resume",
        validators=[Optional(), FileAllowed(["pdf"], "PDFs only!")]
    )

    address = TextAreaField("Address", validators=[Optional(), Length(max=1000)])

    gender = SelectField(
        "Gender",
        choices=[
            (GenderEnum.MALE.value, "Male"),
            (GenderEnum.FEMALE.value, "Female"),
            (GenderEnum.OTHER.value, "Other"),
            (GenderEnum.PREFER_NOT_TO_SAY.value, "Prefer not to say"),
        ],
        validators=[Optional()]
    )

    education_qualification = StringField("Education Qualification", validators=[Optional(), Length(max=200)])

    submit = SubmitField("Register")