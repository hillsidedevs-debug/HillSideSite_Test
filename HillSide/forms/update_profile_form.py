from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField
from wtforms.validators import Length, Optional, Email
from flask_wtf.file import FileField, FileAllowed


class UpdateProfileForm(FlaskForm):
    first_name = StringField(validators=[Length(max=50)])
    last_name = StringField(validators=[Length(max=50)])
    username = StringField(validators=[Length(min=3, max=30)])
    email = StringField(validators=[Email(), Length(max=120)])

    phone_number = StringField(validators=[Optional(), Length(max=20)])

    gender = SelectField(
        choices=[
            ("", "Prefer not to say"),
            ("M", "Male"),
            ("F", "Female"),
            ("Other", "Other"),
            ("Prefer not to say", "Prefer not to say"),
        ],
        validators=[Optional()],
    )

    education_qualification = StringField(
        validators=[Optional(), Length(max=100)]
    )

    address = TextAreaField(
        validators=[Optional(), Length(max=255)]
    )

    photo = FileField(
        validators=[
            Optional(),
            FileAllowed(["jpg", "jpeg", "png"], "Images only!")
        ]
    )

    resume = FileField(
        validators=[
            Optional(),
            FileAllowed(["pdf"], "PDF only!")
        ]
    )
