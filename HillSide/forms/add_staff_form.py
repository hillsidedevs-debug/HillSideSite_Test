from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SubmitField, PasswordField, SelectField, HiddenField
)
from wtforms.validators import DataRequired, Email, Optional, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed
from HillSide.models import GenderEnum, RoleEnum  # import correct path

def enum_choices_from_enum(e):
    # returns list of (value, label) pairs
    return [(member.value, member.name.title().replace('_', ' ')) for member in e]

class AddStaffForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=100)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=100)])

    username = StringField("Username", validators=[DataRequired(), Length(max=150)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=150)])

    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    password_confirm = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')]
    )

    role = SelectField("Role", choices=enum_choices_from_enum(RoleEnum), validators=[DataRequired()])

    phone_number = StringField("Phone Number", validators=[Optional(), Length(max=20)])
    photo = FileField("Profile Photo", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png"], "Images only!")])
    resume = FileField("Resume", validators=[Optional(), FileAllowed(["pdf", "doc", "docx"], "Documents only!")])

    address = TextAreaField("Address", validators=[Optional(), Length(max=2000)])
    gender = SelectField("Gender", choices=[('', '---')] + enum_choices_from_enum(GenderEnum), validators=[Optional()])
    education_qualification = StringField("Education Qualification", validators=[Optional(), Length(max=200)])

    submit = SubmitField("Create Staff Account")
