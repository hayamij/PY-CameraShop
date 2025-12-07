"""
Authentication Routes Blueprint
Login, Register, Logout
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.infrastructure.factory import bcrypt
from app.infrastructure.database.models import UserModel
from app.infrastructure.database.db import db
from app.business.use_cases import (
    RegisterUserUseCase,
    RegisterUserInputData,
    LoginUserUseCase,
    LoginUserInputData
)
from app.adapters.repositories import UserRepositoryAdapter

auth_bp = Blueprint('auth', __name__)

# Initialize repository and use cases
user_repository = UserRepositoryAdapter()
register_use_case = RegisterUserUseCase(user_repository)
login_use_case = LoginUserUseCase(user_repository)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username_or_email = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        if not username_or_email or not password:
            flash('Vui lòng điền đầy đủ thông tin', 'danger')
            return render_template('auth/login.html')
        
        # Find user in database (Infrastructure layer)
        user_model = UserModel.query.filter(
            (UserModel.username == username_or_email) | 
            (UserModel.email == username_or_email)
        ).first()
        
        if user_model and bcrypt.check_password_hash(user_model.password_hash, password):
            if not user_model.is_active:
                flash('Tài khoản đã bị vô hiệu hóa', 'danger')
                return render_template('auth/login.html')
            
            # Login successful
            login_user(user_model, remember=remember)
            
            # Redirect to next page or home
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            # Redirect based on role
            if user_model.role == 'ADMIN':
                flash(f'Chào mừng Admin {user_model.full_name}!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash(f'Chào mừng {user_model.full_name}!', 'success')
                return redirect(url_for('main.index'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page and handler"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        phone_number = request.form.get('phone_number')
        address = request.form.get('address')
        
        # Validation
        if not all([username, email, password, full_name]):
            flash('Vui lòng điền đầy đủ thông tin bắt buộc', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Mật khẩu xác nhận không khớp', 'danger')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Mật khẩu phải có ít nhất 6 ký tự', 'danger')
            return render_template('auth/register.html')
        
        # Hash password (Infrastructure concern)
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Execute use case
        input_data = RegisterUserInputData(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            phone_number=phone_number,
            address=address
        )
        
        output_data = register_use_case.execute(input_data)
        
        if output_data.success:
            flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(output_data.error_message, 'danger')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout handler"""
    logout_user()
    flash('Đã đăng xuất thành công', 'success')
    return redirect(url_for('main.index'))
