from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FloatField, IntegerField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange
from models import User
class StudentRegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    roll_number = StringField('Roll Number', validators=[DataRequired(), Length(min=5, max=50)])
    course = StringField('Course', validators=[DataRequired()])
    branch = StringField('Branch', validators=[DataRequired()])
    semester = IntegerField('Semester', validators=[DataRequired()])
    contact = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    cgpa = FloatField('CGPA', validators=[DataRequired()])
    passing_year = IntegerField('Passing Year', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    resume = FileField('Upload Resume (PDF only)', validators=[FileAllowed(['pdf'], 'PDF only!')])
    submit = SubmitField('Register')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already registered. Please use another email.')

class CompanyRegistrationForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    hr_name = StringField('HR Name', validators=[DataRequired()])
    hr_contact = StringField('HR Contact', validators=[DataRequired(), Length(min=10, max=15)])
    website = StringField('Website')  # Optional field
    description = TextAreaField('Company Description', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register Company')
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already registered.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class PlacementDriveForm(FlaskForm):
    job_title = StringField('Job Title', validators=[DataRequired()])
    job_description = TextAreaField('Job Description', validators=[DataRequired()])
    min_cgpa = FloatField('Minimum CGPA Required', validators=[DataRequired()])
    allowed_branches = StringField('Allowed Branches (comma separated)', validators=[DataRequired()])
    package = StringField('Package (CTC in lakhs)', validators=[DataRequired()])
    location = StringField('Job Location', validators=[DataRequired()])
    application_deadline = DateField('Application Deadline', validators=[DataRequired()])
    drive_date = DateField('Drive Date', validators=[DataRequired()])
    submit = SubmitField('Create Placement Drive')
    
class CompanyProfileForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired(), Length(min=2, max=100)])
    hr_name = StringField('HR Name', validators=[DataRequired(), Length(min=2, max=100)])
    hr_contact = StringField('HR Contact', validators=[DataRequired(), Length(min=10, max=15)])
    website = StringField('Website')
    description = TextAreaField('Company Description', validators=[DataRequired()])
    industry = StringField('Industry', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    logo = FileField('Company Logo', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Update Profile')

class StudentProfileEditForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    contact = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    semester = IntegerField('Semester', validators=[DataRequired(), NumberRange(min=1, max=8)])
    cgpa = FloatField('CGPA', validators=[DataRequired(), NumberRange(min=0, max=10)])
    passing_year = IntegerField('Passing Year', validators=[DataRequired()])
    resume = FileField('Resume (PDF only)', validators=[FileAllowed(['pdf'], 'PDF only!')])
    submit = SubmitField('Update Profile')