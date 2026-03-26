from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
db = SQLAlchemy()
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False)
    company_profile = db.relationship('CompanyProfile', backref='user', uselist=False)
    admin_profile = db.relationship('Admin', backref='user', uselist=False)
class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    full_name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)
    course = db.Column(db.String(100))
    branch = db.Column(db.String(100))
    semester = db.Column(db.Integer)
    contact = db.Column(db.String(15))
    cgpa = db.Column(db.Float)
    passing_year = db.Column(db.Integer)
    resume_path = db.Column(db.String(200))
    applications = db.relationship('Application', backref='student', lazy=True)

class CompanyProfile(db.Model):
    __tablename__ = 'company_profiles'   
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    company_name = db.Column(db.String(100), nullable=False)
    hr_name = db.Column(db.String(100))
    hr_email = db.Column(db.String(120))
    hr_contact = db.Column(db.String(15))
    website = db.Column(db.String(200))
    description = db.Column(db.Text)
    approval_status = db.Column(db.String(20), default='pending')
    is_blacklisted = db.Column(db.Boolean, default=False)
    placement_drives = db.relationship('PlacementDrive', backref='company', lazy=True)

class PlacementDrive(db.Model):
    __tablename__ = 'placement_drives'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company_profiles.id'))
    job_title = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text)
    eligibility_criteria = db.Column(db.String(500))
    min_cgpa = db.Column(db.Float)
    allowed_branches = db.Column(db.String(500))
    package = db.Column(db.String(100))
    location = db.Column(db.String(200))
    application_deadline = db.Column(db.DateTime)
    drive_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')
    applications = db.relationship('Application', backref='drive', lazy=True)

class Application(db.Model):
    __tablename__ = 'applications'  
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'))
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id'))
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='applied')
    remarks = db.Column(db.String(500))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('student_id', 'drive_id', name='unique_application'),)

class Admin(db.Model):
    __tablename__ = 'admins'   
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    department = db.Column(db.String(100), default='Placement Cell')