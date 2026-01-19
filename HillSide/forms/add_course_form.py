from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DateField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange

class CourseForm(FlaskForm):
    title = StringField('Course Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[Optional()])
    duration_weeks = IntegerField('Duration (Weeks)', validators=[Optional(), NumberRange(min=1)])
    total_seats = IntegerField('Total Seats', validators=[Optional(), NumberRange(min=1)])
    
    # Image Upload
    image = FileField('Course Image', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])

    who_is_this_for = TextAreaField('Who is this for?')
    learning_outcomes = TextAreaField('Learning Outcomes')
    course_structure = TextAreaField('Course Structure')

    instructor_name = StringField('Instructor Name')
    instructor_bio = TextAreaField('Instructor Bio')
    faqs = TextAreaField('FAQs')
    
    submit = SubmitField('Add Course')