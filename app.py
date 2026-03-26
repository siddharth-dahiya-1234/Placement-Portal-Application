from flask import Flask, render_template, redirect, url_for, flash, request, abort, jsonify, send_file
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_uploads import UploadSet, configure_uploads, DOCUMENTS
from werkzeug.utils import secure_filename
from models import db, User, StudentProfile, CompanyProfile, PlacementDrive, Application, Admin
from forms import StudentRegistrationForm, CompanyRegistrationForm, LoginForm, PlacementDriveForm, CompanyProfileForm, StudentProfileEditForm
from utils.decorators import admin_required, company_required, student_required, approved_company_required
from datetime import datetime, timedelta
import os
import secrets
import csv
import io
from sqlalchemy import func, desc

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement_portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOADED_RESUMES_DEST'] = 'static/uploads'
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
resumes = UploadSet('resumes', DOCUMENTS)
configure_uploads(app, resumes)

# Ensure upload directory exists
os.makedirs(app.config['UPLOADED_RESUMES_DEST'], exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_admin():
    with app.app_context():
        db.create_all()
        admin_user = User.query.filter_by(email='admin@placement.edu').first()   
        if not admin_user:
            hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin_user = User(email='admin@placement.edu',password_hash=hashed_password,role='admin',is_active=True)
            db.session.add(admin_user)
            db.session.flush()
            admin_profile = Admin(user_id=admin_user.id,department='Placement Cell')
            db.session.add(admin_profile)
            db.session.commit()
            print('='*50)
            print('ADMIN CREATED SUCCESSFULLY!')
            print('Email: admin@placement.edu')
            print('Password: admin123')
            print('='*50)

@app.route('/')
def index():
    # Get statistics for homepage
    total_companies = CompanyProfile.query.count()
    total_students = StudentProfile.query.count()
    total_drives = PlacementDrive.query.filter_by(status='approved').count()
    success_rate = 95  # This could be calculated from actual data
    return render_template('index.html', 
                         total_companies=total_companies,
                         total_students=total_students,
                         total_drives=total_drives,
                         success_rate=success_rate)

@app.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = StudentRegistrationForm()
    
    if form.validate_on_submit():
        try:
            # Check if email already exists
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user:
                flash('This email is already registered. Please use a different email or login.', 'error')
                return render_template('auth/register_student.html', form=form)
            
            # Check if roll number already exists
            existing_student = StudentProfile.query.filter_by(roll_number=form.roll_number.data).first()
            if existing_student:
                flash(f'Roll number {form.roll_number.data} is already registered. Please verify your roll number or contact administration.', 'error')
                return render_template('auth/register_student.html', form=form)
            
            # Check if contact already exists
            existing_contact = StudentProfile.query.filter_by(contact=form.contact.data).first()
            if existing_contact:
                flash('This contact number is already registered. Please use a different number.', 'error')
                return render_template('auth/register_student.html', form=form)
            
            # Create user
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(
                email=form.email.data,
                password_hash=hashed_password,
                role='student',
                is_active=True
            )
            db.session.add(user)
            db.session.flush()  # Get user.id
            
            # Handle resume upload
            resume_filename = None
            if form.resume.data:
                try:
                    # Validate file type
                    if not form.resume.data.filename.endswith('.pdf'):
                        flash('Only PDF files are allowed for resume.', 'error')
                        db.session.rollback()
                        return render_template('auth/register_student.html', form=form)
                    
                    # Validate file size (2MB max)
                    form.resume.data.seek(0, os.SEEK_END)
                    file_size = form.resume.data.tell()
                    form.resume.data.seek(0)
                    
                    if file_size > 2 * 1024 * 1024:  # 2MB in bytes
                        flash('Resume file size must be less than 2MB.', 'error')
                        db.session.rollback()
                        return render_template('auth/register_student.html', form=form)
                    
                    # Save resume
                    resume_filename = resumes.save(form.resume.data, name=f"student_{user.id}_")
                except Exception as e:
                    app.logger.error(f"Resume upload error: {str(e)}")
                    flash('Error uploading resume. Please try again.', 'error')
                    db.session.rollback()
                    return render_template('auth/register_student.html', form=form)
            
            # Create student profile
            student = StudentProfile(
                user_id=user.id,
                full_name=form.full_name.data,
                roll_number=form.roll_number.data,
                course=form.course.data,
                branch=form.branch.data,
                semester=form.semester.data,
                contact=form.contact.data,
                cgpa=form.cgpa.data,
                passing_year=form.passing_year.data,
                resume_path=resume_filename
            )
            db.session.add(student)
            
            # Commit all changes
            db.session.commit()
            
            flash('Congratulations! Registration successful! You can now login.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            
            # Handle specific database errors
            error_str = str(e).lower()
            if 'unique constraint' in error_str or 'duplicate' in error_str:
                if 'roll_number' in error_str:
                    flash(f'Roll number {form.roll_number.data} is already registered. Please verify your roll number.', 'error')
                elif 'email' in error_str:
                    flash('This email is already registered. Please use a different email.', 'error')
                elif 'contact' in error_str:
                    flash('This contact number is already registered. Please use a different number.', 'error')
                else:
                    flash('Registration failed due to duplicate information. Please check your details.', 'error')
            else:
                # Log the actual error for debugging
                app.logger.error(f"Registration error: {str(e)}")
                flash('An unexpected error occurred during registration. Please try again.', 'error')
            
            return render_template('auth/register_student.html', form=form)
    
    return render_template('auth/register_student.html', form=form)

@app.route('/register/company', methods=['GET', 'POST'])
def register_company():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = CompanyRegistrationForm()
    if form.validate_on_submit():
        # Check if email exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('This email is already registered. Please use a different email.', 'error')
            return render_template('auth/register_company.html', form=form)
            
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(email=form.email.data,password_hash=hashed_password,role='company',is_active=True)
        db.session.add(user)
        db.session.flush()
        company = CompanyProfile(
            user_id=user.id,
            company_name=form.company_name.data,
            hr_name=form.hr_name.data,
            hr_email=form.email.data,
            hr_contact=form.hr_contact.data,
            website=form.website.data,
            description=form.description.data,
            approval_status='pending',
            industry='Technology',  # Default value
            location='Remote'  # Default value
        )
        db.session.add(company)
        db.session.commit()
        flash('Company registration submitted! Please wait for admin approval.', 'info')
        return redirect(url_for('login'))
    return render_template('auth/register_company.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact admin.', 'danger')
                return redirect(url_for('login'))
            if user.role == 'company':
                company = CompanyProfile.query.filter_by(user_id=user.id).first()
                if company and company.approval_status != 'approved':
                    flash('Your company account is pending admin approval.', 'warning')
                    return redirect(url_for('login'))
            login_user(user, remember=True)
            flash(f'Welcome back, {user.email}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check email and password.', 'danger')
    return render_template('auth/login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif current_user.role == 'company':
        return redirect(url_for('company_dashboard'))
    elif current_user.role == 'student':
        return redirect(url_for('student_dashboard'))
    else:
        return redirect(url_for('index'))

# ==================== ADMIN ROUTES ====================

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    total_students = StudentProfile.query.count()
    total_companies = CompanyProfile.query.count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()
    pending_companies = CompanyProfile.query.filter_by(approval_status='pending').all()
    pending_drives = PlacementDrive.query.filter_by(status='pending').all()
    
    # Additional stats for dashboard
    approved_companies = CompanyProfile.query.filter_by(approval_status='approved').count()
    approved_drives = PlacementDrive.query.filter_by(status='approved').count()
    recent_applications = Application.query.order_by(Application.application_date.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_students=total_students,
                         total_companies=total_companies,
                         total_drives=total_drives,
                         total_applications=total_applications,
                         pending_companies=pending_companies,
                         pending_drives=pending_drives,
                         approved_companies=approved_companies,
                         approved_drives=approved_drives,
                         recent_applications=recent_applications)
    
@app.route('/admin/companies')
@login_required
@admin_required
def admin_companies():
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    query = CompanyProfile.query.join(User)
    
    if search:
        query = query.filter(CompanyProfile.company_name.contains(search))
    
    companies = query.all()
    
    # Filter by status after query
    if status and status != 'all':
        companies = [c for c in companies if c.approval_status == status]
    
    return render_template('admin/companies.html', companies=companies, search=search, status=status)

@app.route('/admin/company/<int:company_id>')
@login_required
@admin_required
def admin_view_company(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    drives = PlacementDrive.query.filter_by(company_id=company_id).order_by(PlacementDrive.created_at.desc()).all()
    return render_template('admin/view_company.html', company=company, drives=drives)

@app.route('/admin/company/<int:company_id>/approve')
@login_required
@admin_required
def approve_company(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.approval_status = 'approved'
    db.session.commit()
    flash(f'Company "{company.company_name}" has been approved!', 'success')
    return redirect(request.referrer or url_for('admin_companies'))

@app.route('/admin/company/<int:company_id>/reject')
@login_required
@admin_required
def reject_company(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.approval_status = 'rejected'
    db.session.commit()
    flash(f'Company "{company.company_name}" has been rejected.', 'warning')
    return redirect(request.referrer or url_for('admin_companies'))

@app.route('/admin/company/<int:company_id>/toggle-blacklist')
@login_required
@admin_required
def toggle_company_blacklist(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.is_blacklisted = not company.is_blacklisted
    user = User.query.get(company.user_id)
    user.is_active = not user.is_active
    db.session.commit()
    status = 'blacklisted' if company.is_blacklisted else 'activated'
    flash(f'Company "{company.company_name}" has been {status}!', 'success')
    return redirect(request.referrer or url_for('admin_companies'))

@app.route('/admin/company/<int:company_id>/delete')
@login_required
@admin_required
def delete_company(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company_name = company.company_name
    
    # Delete related data
    drives = PlacementDrive.query.filter_by(company_id=company_id).all()
    for drive in drives:
        Application.query.filter_by(drive_id=drive.id).delete()
        db.session.delete(drive)
    
    user = User.query.get(company.user_id)
    db.session.delete(company)
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Company "{company_name}" and all related data have been deleted.', 'success')
    return redirect(url_for('admin_companies'))

@app.route('/admin/drives')
@login_required
@admin_required
def admin_drives():
    drives = PlacementDrive.query.order_by(PlacementDrive.created_at.desc()).all()
    
    # Create JSON-serializable data
    drives_data = []
    for drive in drives:
        drives_data.append({
            'id': drive.id,
            'job_title': drive.job_title,
            'company_name': drive.company.company_name,
            'company_id': drive.company.id,
            'package': drive.package,
            'location': drive.location,
            'min_cgpa': drive.min_cgpa,
            'allowed_branches': drive.allowed_branches,
            'status': drive.status,
            'application_deadline': drive.application_deadline.strftime('%Y-%m-%d') if drive.application_deadline else '',
            'drive_date': drive.drive_date.strftime('%Y-%m-%d') if drive.drive_date else '',
            'created_at': drive.created_at.strftime('%Y-%m-%d %H:%M:%S') if drive.created_at else '',
            'job_description': drive.job_description[:200] if drive.job_description else ''  # Truncate for JS
        })
    
    return render_template('admin/drives.html', drives=drives, drives_data=drives_data)

@app.route('/admin/drive/<int:drive_id>')
@login_required
@admin_required
def admin_view_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    applications = Application.query.filter_by(drive_id=drive_id).join(StudentProfile).all()
    return render_template('admin/view_drive.html', drive=drive, applications=applications)

@app.route('/admin/drive/<int:drive_id>/approve')
@login_required
@admin_required
def approve_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = 'approved'
    db.session.commit()
    flash(f'Drive "{drive.job_title}" has been approved!', 'success')
    return redirect(request.referrer or url_for('admin_drives'))

@app.route('/admin/drive/<int:drive_id>/reject')
@login_required
@admin_required
def reject_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = 'rejected'
    db.session.commit()
    flash(f'Drive "{drive.job_title}" has been rejected.', 'warning')
    return redirect(request.referrer or url_for('admin_drives'))

@app.route('/admin/drive/<int:drive_id>/close')
@login_required
@admin_required
def admin_close_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = 'closed'
    db.session.commit()
    flash(f'Drive "{drive.job_title}" has been closed.', 'success')
    return redirect(request.referrer or url_for('admin_drives'))

@app.route('/admin/drive/<int:drive_id>/delete')
@login_required
@admin_required
def admin_delete_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    job_title = drive.job_title
    Application.query.filter_by(drive_id=drive_id).delete()
    db.session.delete(drive)
    db.session.commit()
    flash(f'Drive "{job_title}" has been deleted.', 'success')
    return redirect(url_for('admin_drives'))

@app.route('/admin/students')
@login_required
@admin_required
def admin_students():
    search = request.args.get('search', '')
    query = StudentProfile.query.join(User)
    
    if search:
        query = query.filter(
            (StudentProfile.full_name.contains(search)) |
            (StudentProfile.roll_number.contains(search)) |
            (StudentProfile.contact.contains(search))
        )
    
    students = query.all()
    return render_template('admin/students.html', students=students, search=search)

@app.route('/admin/student/<int:student_id>')
@login_required
@admin_required
def admin_view_student(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    applications = Application.query.filter_by(student_id=student_id).join(PlacementDrive).all()
    return render_template('admin/view_student.html', student=student, applications=applications)

@app.route('/admin/student/<int:student_id>/toggle-status')
@login_required
@admin_required
def toggle_student_status(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    user = User.query.get(student.user_id)
    user.is_active = not user.is_active
    db.session.commit()
    status = 'deactivated' if not user.is_active else 'activated'
    flash(f'Student "{student.full_name}" has been {status}!', 'success')
    return redirect(request.referrer or url_for('admin_students'))

@app.route('/admin/student/<int:student_id>/delete')
@login_required
@admin_required
def delete_student(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    student_name = student.full_name
    
    # Delete applications
    Application.query.filter_by(student_id=student_id).delete()
    
    user = User.query.get(student.user_id)
    db.session.delete(student)
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Student "{student_name}" has been deleted.', 'success')
    return redirect(url_for('admin_students'))

@app.route('/admin/reports')
@login_required
@admin_required
def admin_reports():
    # Get statistics for reports
    total_students = StudentProfile.query.count()
    total_companies = CompanyProfile.query.count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()
    
    # Drives by status
    approved_drives = PlacementDrive.query.filter_by(status='approved').count()
    pending_drives = PlacementDrive.query.filter_by(status='pending').count()
    closed_drives = PlacementDrive.query.filter_by(status='closed').count()
    rejected_drives = PlacementDrive.query.filter_by(status='rejected').count()
    
    # Applications by status
    applied_apps = Application.query.filter_by(status='applied').count()
    shortlisted_apps = Application.query.filter_by(status='shortlisted').count()
    selected_apps = Application.query.filter_by(status='selected').count()
    rejected_apps = Application.query.filter_by(status='rejected').count()
    
    # Monthly application trends (last 6 months)
    monthly_apps = []
    for i in range(5, -1, -1):
        date = datetime.now() - timedelta(days=30*i)
        count = Application.query.filter(
            func.strftime('%Y-%m', Application.application_date) == date.strftime('%Y-%m')
        ).count()
        monthly_apps.append({
            'month': date.strftime('%b %Y'),
            'count': count
        })
    
    return render_template('admin/reports.html',
                         total_students=total_students,
                         total_companies=total_companies,
                         total_drives=total_drives,
                         total_applications=total_applications,
                         approved_drives=approved_drives,
                         pending_drives=pending_drives,
                         closed_drives=closed_drives,
                         rejected_drives=rejected_drives,
                         applied_apps=applied_apps,
                         shortlisted_apps=shortlisted_apps,
                         selected_apps=selected_apps,
                         rejected_apps=rejected_apps,
                         monthly_apps=monthly_apps)

@app.route('/admin/reports/export')
@login_required
@admin_required
def export_reports():
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(['Report Type', 'Metric', 'Value', 'Date'])
    
    # Write data
    writer.writerow(['Students', 'Total', StudentProfile.query.count(), datetime.now().strftime('%Y-%m-%d')])
    writer.writerow(['Companies', 'Total', CompanyProfile.query.count(), datetime.now().strftime('%Y-%m-%d')])
    writer.writerow(['Drives', 'Total', PlacementDrive.query.count(), datetime.now().strftime('%Y-%m-%d')])
    writer.writerow(['Applications', 'Total', Application.query.count(), datetime.now().strftime('%Y-%m-%d')])
    
    # Move to beginning of file
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'report_{datetime.now().strftime("%Y%m%d")}.csv'
    )

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_settings():
    admin = Admin.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        # Update admin profile
        admin.department = request.form.get('department', admin.department)
        
        # Update password if provided
        current_pwd = request.form.get('current_password')
        new_pwd = request.form.get('new_password')
        confirm_pwd = request.form.get('confirm_password')
        
        if current_pwd and new_pwd and confirm_pwd:
            if bcrypt.check_password_hash(current_user.password_hash, current_pwd):
                if new_pwd == confirm_pwd:
                    current_user.password_hash = bcrypt.generate_password_hash(new_pwd).decode('utf-8')
                    flash('Password updated successfully!', 'success')
                else:
                    flash('New passwords do not match.', 'error')
            else:
                flash('Current password is incorrect.', 'error')
        
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin_settings'))
    
    return render_template('admin/settings.html', admin=admin)

# ==================== COMPANY ROUTES ====================

@app.route('/company/dashboard')
@login_required
@company_required
@approved_company_required
def company_dashboard():
    company = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    drives = PlacementDrive.query.filter_by(company_id=company.id).order_by(PlacementDrive.created_at.desc()).all()
    drive_stats = []
    total_applications = 0
    selected_candidates = 0
    
    for drive in drives:
        app_count = Application.query.filter_by(drive_id=drive.id).count()
        selected_count = Application.query.filter_by(drive_id=drive.id, status='selected').count()
        total_applications += app_count
        selected_candidates += selected_count
        drive_stats.append({
            'drive': drive,
            'applications': app_count,
            'selected': selected_count,
            'shortlisted': Application.query.filter_by(drive_id=drive.id, status='shortlisted').count(),
            'rejected': Application.query.filter_by(drive_id=drive.id, status='rejected').count()
        })
    
    active_drives = PlacementDrive.query.filter_by(company_id=company.id, status='approved').count()
    recent_applications = Application.query.join(PlacementDrive).filter(
        PlacementDrive.company_id == company.id
    ).order_by(Application.application_date.desc()).limit(5).all()
    
    # Calculate percentages
    active_percentage = (active_drives / len(drives) * 100) if drives else 0
    selection_rate = (selected_candidates / total_applications * 100) if total_applications > 0 else 0
    
    return render_template('company/dashboard.html', 
                         company=company, 
                         drive_stats=drive_stats,
                         total_drives=len(drives),
                         active_drives=active_drives,
                         total_applications=total_applications,
                         selected_candidates=selected_candidates,
                         active_percentage=round(active_percentage),
                         selection_rate=round(selection_rate),
                         recent_applications=recent_applications)

@app.route('/company/create-drive', methods=['GET', 'POST'])
@login_required
@company_required
@approved_company_required
def create_drive():
    form = PlacementDriveForm()
    company = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    
    if form.validate_on_submit():
        try:
            drive = PlacementDrive(
                company_id=company.id,
                job_title=form.job_title.data,
                job_description=form.job_description.data,
                min_cgpa=form.min_cgpa.data,
                allowed_branches=form.allowed_branches.data,
                package=form.package.data,
                location=form.location.data,
                application_deadline=form.application_deadline.data,
                drive_date=form.drive_date.data,
                status='pending',
                created_at=datetime.now()
            )
            db.session.add(drive)
            db.session.commit()
            flash('Placement drive created! Waiting for admin approval.', 'success')
            return redirect(url_for('company_dashboard'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating drive: {str(e)}")
            flash('An error occurred while creating the drive. Please try again.', 'error')
            return render_template('company/create_drive.html', form=form, company=company)
    
    return render_template('company/create_drive.html', form=form, company=company)

@app.route('/company/drive/<int:drive_id>')
@login_required
@company_required
def view_drive_applications(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    company = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    if drive.company_id != company.id:
        abort(403)
    applications = Application.query.filter_by(drive_id=drive_id).join(StudentProfile).all()
    return render_template('company/drive_applications.html', drive=drive, applications=applications)

@app.route('/company/application/<int:app_id>/status', methods=['POST'])
@login_required
@company_required
def update_application_status(app_id):
    application = Application.query.get_or_404(app_id)
    new_status = request.form.get('status')
    application.status = new_status
    db.session.commit()
    flash('Application status updated!', 'success')
    return redirect(url_for('view_drive_applications', drive_id=application.drive_id))

@app.route('/company/application/<int:app_id>/shortlist', methods=['POST'])
@login_required
@company_required
def shortlist_application(app_id):
    application = Application.query.get_or_404(app_id)
    application.status = 'shortlisted'
    db.session.commit()
    flash('Application shortlisted!', 'success')
    return redirect(request.referrer or url_for('view_drive_applications', drive_id=application.drive_id))

@app.route('/company/application/<int:app_id>/select', methods=['POST'])
@login_required
@company_required
def select_application(app_id):
    application = Application.query.get_or_404(app_id)
    application.status = 'selected'
    db.session.commit()
    flash('Candidate selected!', 'success')
    return redirect(request.referrer or url_for('view_drive_applications', drive_id=application.drive_id))

@app.route('/company/application/<int:app_id>/reject', methods=['POST'])
@login_required
@company_required
def reject_application(app_id):
    application = Application.query.get_or_404(app_id)
    application.status = 'rejected'
    db.session.commit()
    flash('Application rejected.', 'info')
    return redirect(request.referrer or url_for('view_drive_applications', drive_id=application.drive_id))

@app.route('/company/drive/<int:drive_id>/edit', methods=['GET', 'POST'])
@login_required
@company_required
def edit_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    company = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    
    if drive.company_id != company.id:
        abort(403)
    
    form = PlacementDriveForm(obj=drive)
    
    if form.validate_on_submit():
        drive.job_title = form.job_title.data
        drive.job_description = form.job_description.data
        drive.min_cgpa = form.min_cgpa.data
        drive.allowed_branches = form.allowed_branches.data
        drive.package = form.package.data
        drive.location = form.location.data
        drive.application_deadline = form.application_deadline.data
        drive.drive_date = form.drive_date.data
        drive.status = 'pending'  # Reset to pending for re-approval
        
        db.session.commit()
        flash('Drive updated successfully! Waiting for admin re-approval.', 'success')
        return redirect(url_for('company_dashboard'))
    
    return render_template('company/edit_drive.html', form=form, drive=drive)

@app.route('/company/drive/<int:drive_id>/close')
@login_required
@company_required
def close_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    company = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    
    if drive.company_id != company.id:
        abort(403)
        
    drive.status = 'closed'
    db.session.commit()
    flash('Drive closed successfully!', 'success')
    return redirect(request.referrer or url_for('company_dashboard'))

@app.route('/company/drive/<int:drive_id>/delete')
@login_required
@company_required
def delete_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    company = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    
    if drive.company_id != company.id:
        abort(403)
    
    Application.query.filter_by(drive_id=drive_id).delete()
    db.session.delete(drive)
    db.session.commit()
    
    flash('Drive deleted successfully!', 'success')
    return redirect(url_for('company_dashboard'))

@app.route('/company/drive/<int:drive_id>/duplicate')
@login_required
@company_required
def duplicate_drive(drive_id):
    original = PlacementDrive.query.get_or_404(drive_id)
    company = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    
    if original.company_id != company.id:
        abort(403)
    
    new_drive = PlacementDrive(
        company_id=company.id,
        job_title=f"{original.job_title} (Copy)",
        job_description=original.job_description,
        min_cgpa=original.min_cgpa,
        allowed_branches=original.allowed_branches,
        package=original.package,
        location=original.location,
        application_deadline=original.application_deadline,
        drive_date=original.drive_date,
        max_applications=original.max_applications,
        status='pending',
        created_at=datetime.now()
    )
    
    db.session.add(new_drive)
    db.session.commit()
    
    flash('Drive duplicated successfully! Please review and submit.', 'success')
    return redirect(url_for('edit_drive', drive_id=new_drive.id))

@app.route('/company/drive/<int:drive_id>/export')
@login_required
@company_required
def export_applications(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    company = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    
    if drive.company_id != company.id:
        abort(403)
    
    applications = Application.query.filter_by(drive_id=drive_id).join(StudentProfile).all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow(['Roll Number', 'Student Name', 'Email', 'Course', 'Branch', 'CGPA', 'Applied Date', 'Status'])
    
    # Data
    for app in applications:
        writer.writerow([
            app.student.roll_number,
            app.student.full_name,
            app.student.user.email,
            app.student.course,
            app.student.branch,
            app.student.cgpa,
            app.application_date.strftime('%Y-%m-%d'),
            app.status
        ])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'applications_{drive.job_title}_{datetime.now().strftime("%Y%m%d")}.csv'
    )

@app.route('/company/candidates')
@login_required
@company_required
@approved_company_required
def browse_candidates():
    company = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    
    # Get filter parameters
    branch = request.args.get('branch', '')
    min_cgpa = request.args.get('min_cgpa', 0, type=float)
    search = request.args.get('search', '')
    
    query = StudentProfile.query.join(User).filter(User.is_active == True)
    
    if search:
        query = query.filter(
            (StudentProfile.full_name.contains(search)) |
            (StudentProfile.roll_number.contains(search))
        )
    
    if branch:
        query = query.filter(StudentProfile.branch == branch)
    
    if min_cgpa:
        query = query.filter(StudentProfile.cgpa >= min_cgpa)
    
    students = query.order_by(StudentProfile.cgpa.desc()).all()
    
    # Get all unique branches for filter
    branches = db.session.query(StudentProfile.branch).distinct().all()
    branches = [b[0] for b in branches if b[0]]
    
    return render_template('company/candidates.html', 
                         students=students, 
                         branches=branches,
                         selected_branch=branch,
                         min_cgpa=min_cgpa,
                         search=search)

@app.route('/company/candidate/<int:student_id>')
@login_required
@company_required
def view_candidate(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    return render_template('company/view_candidate.html', student=student)

@app.route('/company/schedule-interview', methods=['POST'])
@login_required
@company_required
def schedule_interview():
    application_id = request.form.get('application_id')
    interview_date = request.form.get('interview_date')
    interview_time = request.form.get('interview_time')
    interview_mode = request.form.get('interview_mode')
    interview_link = request.form.get('interview_link')
    
    # Here you would create an Interview model and save it
    # For now, just flash a message
    flash(f'Interview scheduled for {interview_date} at {interview_time} via {interview_mode}', 'success')
    return redirect(request.referrer or url_for('company_dashboard'))

@app.route('/company/profile', methods=['GET', 'POST'])
@login_required
@company_required
def company_profile():
    company = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    form = CompanyProfileForm(obj=company)
    
    if form.validate_on_submit():
        company.company_name = form.company_name.data
        company.hr_name = form.hr_name.data
        company.hr_contact = form.hr_contact.data
        company.website = form.website.data
        company.description = form.description.data
        company.industry = form.industry.data
        company.location = form.location.data
        
        # Handle logo upload
        if form.logo.data:
            logo_filename = resumes.save(form.logo.data, name=f"company_{company.id}_logo")
            company.logo = logo_filename
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('company_profile'))
    
    return render_template('company/profile.html', form=form, company=company)

@app.route('/company/settings', methods=['GET', 'POST'])
@login_required
@company_required
def company_settings():
    if request.method == 'POST':
        # Update password
        current_pwd = request.form.get('current_password')
        new_pwd = request.form.get('new_password')
        confirm_pwd = request.form.get('confirm_password')
        
        if current_pwd and new_pwd and confirm_pwd:
            if bcrypt.check_password_hash(current_user.password_hash, current_pwd):
                if new_pwd == confirm_pwd:
                    current_user.password_hash = bcrypt.generate_password_hash(new_pwd).decode('utf-8')
                    db.session.commit()
                    flash('Password updated successfully!', 'success')
                else:
                    flash('New passwords do not match.', 'error')
            else:
                flash('Current password is incorrect.', 'error')
        
        # Update notification preferences
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('company_settings'))
    
    return render_template('company/settings.html')

# ==================== STUDENT ROUTES ====================

@app.route('/student/dashboard')
@login_required
@student_required
def student_dashboard():
    student = StudentProfile.query.filter_by(user_id=current_user.id).first()
    approved_drives = PlacementDrive.query.filter(
        PlacementDrive.status == 'approved',
        PlacementDrive.application_deadline >= datetime.today()).order_by(PlacementDrive.application_deadline).all()
    
    eligible_drives = []
    upcoming_deadlines = 0
    
    for drive in approved_drives:
        if drive.min_cgpa and student.cgpa < drive.min_cgpa:
            continue
        if drive.allowed_branches:
            allowed = [b.strip() for b in drive.allowed_branches.split(',')]
            if student.branch not in allowed:
                continue
        already_applied = Application.query.filter_by(student_id=student.id,drive_id=drive.id).first()
        
        # Check if deadline is within 3 days
        if drive.application_deadline <= datetime.today() + timedelta(days=3):
            upcoming_deadlines += 1
            
        eligible_drives.append({
            'drive': drive,
            'can_apply': not already_applied,
            'applied': already_applied is not None
        })
    
    applications = Application.query.filter_by(
        student_id=student.id
    ).join(PlacementDrive).order_by(Application.application_date.desc()).all()
    
    # Statistics
    total_applications = len(applications)
    shortlisted = sum(1 for app in applications if app.status == 'shortlisted')
    selected = sum(1 for app in applications if app.status == 'selected')
    
    return render_template('student/dashboard.html',
                         student=student,
                         eligible_drives=eligible_drives,
                         applications=applications,
                         total_applications=total_applications,
                         shortlisted=shortlisted,
                         selected=selected,
                         upcoming_deadlines=upcoming_deadlines)

@app.route('/student/drive/<int:drive_id>/apply')
@login_required
@student_required
def apply_drive(drive_id):
    student = StudentProfile.query.filter_by(user_id=current_user.id).first()
    drive = PlacementDrive.query.get_or_404(drive_id)
    
    existing = Application.query.filter_by(student_id=student.id,drive_id=drive_id).first()
    if existing:
        flash('You have already applied for this drive!', 'warning')
        return redirect(url_for('student_dashboard'))
    
    if drive.application_deadline < datetime.today():
        flash('Sorry, the application deadline has passed!', 'danger')
        return redirect(url_for('student_dashboard'))
    
    if drive.status != 'approved':
        flash('This drive is not currently accepting applications.', 'danger')
        return redirect(url_for('student_dashboard'))
    
    application = Application(student_id=student.id,drive_id=drive_id,status='applied')
    db.session.add(application)
    db.session.commit()
    
    flash('Successfully applied for the drive! Good luck!', 'success')
    return redirect(url_for('student_dashboard'))

@app.route('/student/profile', methods=['GET', 'POST'])
@login_required
@student_required
def student_profile():
    student = StudentProfile.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        student.full_name = request.form.get('full_name')
        student.contact = request.form.get('contact')
        student.semester = request.form.get('semester')
        student.cgpa = request.form.get('cgpa')
        student.passing_year = request.form.get('passing_year')
        
        # Handle resume upload
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename:
                if not file.filename.endswith('.pdf'):
                    flash('Only PDF files are allowed for resume.', 'error')
                    return redirect(url_for('student_profile'))
                
                # Delete old resume if exists
                if student.resume_path:
                    old_file = os.path.join(app.config['UPLOADED_RESUMES_DEST'], student.resume_path)
                    if os.path.exists(old_file):
                        os.remove(old_file)
                
                filename = resumes.save(file, name=f"student_{student.id}_")
                student.resume_path = filename
                flash('Resume uploaded successfully!', 'success')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student_profile'))
    
    # Get statistics for profile page
    applications = Application.query.filter_by(student_id=student.id).all()
    total_apps = len(applications)
    shortlisted = sum(1 for app in applications if app.status == 'shortlisted')
    selected = sum(1 for app in applications if app.status == 'selected')
    
    return render_template('student/profile.html', 
                         student=student,
                         applications=applications,
                         total_apps=total_apps,
                         shortlisted=shortlisted,
                         selected=selected)

@app.route('/student/applications')
@login_required
@student_required
def student_applications():
    student = StudentProfile.query.filter_by(user_id=current_user.id).first()
    applications = Application.query.filter_by(
        student_id=student.id
    ).join(PlacementDrive).order_by(Application.application_date.desc()).all()
    
    return render_template('student/applications.html', applications=applications)

@app.route('/student/resume/download')
@login_required
@student_required
def download_resume():
    student = StudentProfile.query.filter_by(user_id=current_user.id).first()
    
    if not student.resume_path:
        flash('No resume found.', 'error')
        return redirect(url_for('student_profile'))
    
    file_path = os.path.join(app.config['UPLOADED_RESUMES_DEST'], student.resume_path)
    
    if not os.path.exists(file_path):
        flash('Resume file not found.', 'error')
        return redirect(url_for('student_profile'))
    
    return send_file(file_path, as_attachment=True, download_name=f"{student.full_name}_Resume.pdf")

@app.route('/student/resume/delete')
@login_required
@student_required
def delete_resume():
    student = StudentProfile.query.filter_by(user_id=current_user.id).first()
    
    if student.resume_path:
        file_path = os.path.join(app.config['UPLOADED_RESUMES_DEST'], student.resume_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        student.resume_path = None
        db.session.commit()
        flash('Resume deleted successfully!', 'success')
    else:
        flash('No resume to delete.', 'info')
    
    return redirect(url_for('student_profile'))

@app.route('/student/settings', methods=['GET', 'POST'])
@login_required
@student_required
def student_settings():
    if request.method == 'POST':
        # Update password
        current_pwd = request.form.get('current_password')
        new_pwd = request.form.get('new_password')
        confirm_pwd = request.form.get('confirm_password')
        
        if current_pwd and new_pwd and confirm_pwd:
            if bcrypt.check_password_hash(current_user.password_hash, current_pwd):
                if new_pwd == confirm_pwd:
                    current_user.password_hash = bcrypt.generate_password_hash(new_pwd).decode('utf-8')
                    db.session.commit()
                    flash('Password updated successfully!', 'success')
                else:
                    flash('New passwords do not match.', 'error')
            else:
                flash('Current password is incorrect.', 'error')
        
        # Update notification preferences
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('student_settings'))
    
    return render_template('student/settings.html')

# ==================== SHARED ROUTES ====================

@app.route('/notifications')
@login_required
def notifications():
    # This would fetch notifications from a Notification model
    # For now, return empty list
    notifications = []
    return render_template('notifications.html', notifications=notifications)

@app.route('/notifications/mark-read', methods=['POST'])
@login_required
def mark_notifications_read():
    # Mark all notifications as read
    flash('All notifications marked as read.', 'success')
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    results = []
    
    if current_user.role == 'student':
        # Search drives
        drives = PlacementDrive.query.filter(
            PlacementDrive.status == 'approved',
            PlacementDrive.job_title.contains(query) |
            PlacementDrive.company.has(CompanyProfile.company_name.contains(query))
        ).all()
        results = drives
    
    elif current_user.role == 'company':
        # Search candidates
        students = StudentProfile.query.filter(
            StudentProfile.full_name.contains(query) |
            StudentProfile.branch.contains(query)
        ).all()
        results = students
    
    return render_template('search_results.html', results=results, query=query)

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

@app.route('/error/404')
def error_404_preview():
    """Preview 404 error page"""
    return render_template('errors/404.html'), 404

@app.route('/error/403')
def error_403_preview():
    """Preview 403 error page"""
    return render_template('errors/403.html'), 403

@app.route('/error/500')
def error_500_preview():
    """Preview 500 error page"""
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)