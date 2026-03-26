from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Oops! This page is only for administrators.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def company_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'company':
            flash('This page is only for company representatives.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            flash('This page is only for students.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def approved_company_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'company':
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))
        from models import CompanyProfile
        company = CompanyProfile.query.filter_by(user_id=current_user.id).first()
        if not company or company.approval_status != 'approved':
            flash('Your company account is waiting for admin approval.', 'warning')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function