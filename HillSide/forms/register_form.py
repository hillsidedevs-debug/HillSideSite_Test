from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SubmitField, PasswordField,
    SelectField
)
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Email, Optional, EqualTo
from HillSide.models import GenderEnum  # import your enum


class RegisterForm(FlaskForm):

    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])

    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password_confirm = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')]
    )
    phone_number = StringField("Phone Number", validators=[Optional()])

    photo = FileField(
        "Profile Photo",
        validators=[Optional(), FileAllowed(["jpg", "jpeg", "png"], "Images only!")]
    )

    resume = FileField(
        "Resume",
        validators=[Optional(), FileAllowed(["pdf", "doc", "docx"], "Documents only!")]
    )

    address = TextAreaField("Address", validators=[Optional()])

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

    education_qualification = StringField("Education Qualification", validators=[Optional()])

    submit = SubmitField("Register")