"""
Authentication Routes - HTTP API Adapter Layer
Clean Architecture: Controllers orchestrate only, no business logic
"""
from flask import Blueprint, request, jsonify, session
import bcrypt

from ...business.use_cases.register_user_use_case import (
    RegisterUserUseCase,
    RegisterUserInputData,
    RegisterUserOutputData
)
from ...business.use_cases.login_user_use_case import (
    LoginUserUseCase,
    LoginUserInputData,
    LoginUserOutputData
)
from ...business.use_cases.get_user_use_case import GetUserUseCase, GetUserInputData
from ...business.ports import IUserRepository


# Blueprint definition
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


# Dependency injection will be done via blueprint registration
# These will be set by the factory
_register_use_case: RegisterUserUseCase = None
_login_use_case: LoginUserUseCase = None
_get_user_use_case: GetUserUseCase = None
_user_repository: IUserRepository = None


def init_auth_routes(register_uc: RegisterUserUseCase, 
                     login_uc: LoginUserUseCase,
                     get_user_uc: GetUserUseCase,
                     user_repo: IUserRepository):
    """Initialize authentication routes with use case dependencies."""
    global _register_use_case, _login_use_case, _get_user_use_case, _user_repository
    _register_use_case = register_uc
    _login_use_case = login_uc
    _get_user_use_case = get_user_uc
    _user_repository = user_repo


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register new user endpoint
    
    POST /api/auth/register
    Body: {
        "username": "string",
        "email": "string",
        "password": "string",
        "full_name": "string",
        "phone_number": "string" (optional),
        "address": "string" (optional)
    }
    
    Returns:
        201: {"success": true, "user_id": int}
        400: {"success": false, "error": "message"}
    """
    try:
        # Debug: Check repository session
        print(f"DEBUG Register: Repository session = {_user_repository._session}")
        print(f"DEBUG Register: Session bind = {_user_repository._session.bind}")
        print(f"DEBUG Register: DB URL = {_user_repository._session.bind.url}")
        
        # Parse request JSON
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'full_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Hash password (Infrastructure concern) - using bcrypt
        password = data['password'].encode('utf-8')
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password, salt).decode('utf-8')
        
        # Map HTTP request to Use Case Input
        input_data = RegisterUserInputData(
            username=data['username'],
            email=data['email'],
            password_hash=password_hash,
            full_name=data['full_name'],
            phone_number=data.get('phone_number'),
            address=data.get('address')
        )
        
        # Execute use case
        output = _register_use_case.execute(input_data)
        
        # Map Use Case Output to HTTP Response
        if output.success:
            return jsonify({
                'success': True,
                'user_id': output.user_id,
                'message': 'Registration successful'
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': output.error_message
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint
    
    POST /api/auth/login
    Body: {
        "username": "string",  // Can be username or email
        "password": "string"
    }
    
    Returns:
        200: {"success": true, "user": {...}}
        401: {"success": false, "error": "message"}
    """
    try:
        # Debug: Check repository session
        print(f"DEBUG Login: Repository session = {_user_repository._session}")
        print(f"DEBUG Login: Session bind = {_user_repository._session.bind}")
        print(f"DEBUG Login: DB URL = {_user_repository._session.bind.url}")
        
        # Parse request JSON
        data = request.get_json()
        
        # Validate required fields
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'error': 'Username and password are required'
            }), 400
        
        username_or_email = data['username']
        password = data['password']
        
        # First, execute use case to get user info
        # Note: Use case doesn't verify password (no bcrypt in business layer)
        input_data = LoginUserInputData(
            username_or_email=username_or_email,
            password_hash=''  # Placeholder, not used in use case
        )
        
        output = _login_use_case.execute(input_data)
        
        if not output.success:
            return jsonify({
                'success': False,
                'error': output.error_message
            }), 401
        
        # Now verify password (Infrastructure concern)
        # Get user entity from repository to access password_hash
        user = _user_repository.find_by_id(output.user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 401
        
        # Verify password hash using bcrypt
        password_bytes = password.encode('utf-8')
        stored_hash_bytes = user.password_hash.encode('utf-8')
        if not bcrypt.checkpw(password_bytes, stored_hash_bytes):
            return jsonify({
                'success': False,
                'error': 'Invalid username or password'
            }), 401
        
        # Store user session
        session['user_id'] = output.user_id
        session['username'] = output.username
        session['role'] = output.role
        
        # Return success response
        return jsonify({
            'success': True,
            'user': {
                'id': output.user_id,
                'username': output.username,
                'role': output.role,
                'full_name': user.full_name,
                'email': user.email.address
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    User logout endpoint
    
    POST /api/auth/logout
    
    Returns:
        200: {"success": true, "message": "Logged out"}
    """
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """
    Get current authenticated user
    
    GET /api/auth/me
    
    Returns:
        200: {"success": true, "user": {...}}
        401: {"success": false, "error": "Not authenticated"}
    """
    try:
        # Check if user is logged in
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'Not authenticated'
            }), 401
        
        # Get user details
        input_data = GetUserInputData(user_id)
        output = _get_user_use_case.execute(input_data)
        
        if not output.success:
            session.clear()  # Clear invalid session
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 401
        
        return jsonify({
            'success': True,
            'user': {
                'id': output.user_id,
                'username': output.username,
                'email': output.email,
                'full_name': output.full_name,
                'role': output.role,
                'phone_number': output.phone_number,
                'address': output.address,
                'is_active': output.is_active
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500
