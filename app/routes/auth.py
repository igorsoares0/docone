from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db
from app.models.user import User
from app.utils.validators import is_valid_email, is_valid_password

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('documents.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()

        # Validate email
        is_valid, result = is_valid_email(email)
        if not is_valid:
            flash(f'Invalid email: {result}', 'danger')
            return render_template('auth/register.html')

        email = result  # Use normalized email

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please login instead.', 'warning')
            return redirect(url_for('auth.login'))

        # Validate password
        is_valid, message = is_valid_password(password)
        if not is_valid:
            flash(message, 'danger')
            return render_template('auth/register.html')

        # Check password confirmation
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        # Create new user
        user = User(email=email, full_name=full_name)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('documents.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')

        if not user.is_active:
            flash('Your account has been deactivated.', 'warning')
            return render_template('auth/login.html')

        login_user(user, remember=remember)
        flash(f'Welcome back, {user.full_name or user.email}!', 'success')

        # Redirect to next page if specified
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)

        return redirect(url_for('documents.dashboard'))

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
