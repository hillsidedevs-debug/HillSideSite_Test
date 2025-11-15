from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class AddStaffForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = HiddenField(default='staff')
#     course_ids = SelectMultipleField(
#             'Assign to Courses (Required)',
#             coerce=int,
#             choices=[],
#             validators=[DataRequired()]
#     )
    submit = SubmitField()