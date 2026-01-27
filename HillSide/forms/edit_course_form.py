# forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DateField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

class EditCourseForm(FlaskForm):
    title = StringField(
        'Course Title',
        validators=[DataRequired(), Length(max=150)]
    )
    description = TextAreaField(
        'Description',
        validators=[Optional(), Length(max=5000)]
    )
    start_date = DateField(
        'Start Date',
        validators=[Optional()],
        format='%Y-%m-%d'
    )
    duration_weeks = IntegerField(
        'Duration (weeks)',
        validators=[Optional(), NumberRange(min=1)]
    )
    total_seats = IntegerField(
        'Total Seats',
        validators=[Optional(), NumberRange(min=1)]
    )
    who_is_this_for = TextAreaField(
        'Who this course is for',
        validators=[Optional()]
    )
    learning_outcomes = TextAreaField(
        'Learning outcomes',
        validators=[Optional()]
    )
    course_structure = TextAreaField(
        'Course structure',
        validators=[Optional()]
    )
    instructor_name = StringField(
        'Instructor Name',
        validators=[Optional(), Length(max=150)]
    )
    instructor_bio = TextAreaField(
        'Instructor Bio',
        validators=[Optional()]
    )
    faqs = TextAreaField(
        'FAQs',
        validators=[Optional()],
        description="One per line. Format: Question?|Answer"
    )
    image = FileField(
        'Course Photo',
        validators=[
            FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Only images are allowed!')
        ]
    )

    submit = SubmitField('Save Changes')