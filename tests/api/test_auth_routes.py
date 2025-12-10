"""
API Integration Tests for Authentication Routes
Tests HTTP endpoints end-to-end with real Flask app
"""
import pytest
import json


@pytest.fixture
def registered_user(client, clean_db, sample_user_data):
    """Create and return a registered user"""
    response = client.post(
        '/api/auth/register',
        data=json.dumps(sample_user_data),
        content_type='application/json'
    )
    if response.status_code == 201:
        data = json.loads(response.data)
        return {**sample_user_data, 'user_id': data['user_id']}
    return None


class TestRegisterEndpoint:
    """Test POST /api/auth/register"""
    
    def test_register_with_all_fields_success(self, client, sample_user_data):
        """TC1: Register with all fields should succeed"""
        response = client.post(
            '/api/auth/register',
            data=json.dumps(sample_user_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'user_id' in data
        assert data['user_id'] > 0
        assert data['message'] == 'Registration successful'
    
    def test_register_with_minimal_fields_success(self, client):
        """TC2: Register with only required fields"""
        minimal_data = {
            'username': 'minimaluser',
            'email': 'minimal@example.com',
            'password': 'Password123',
            'full_name': 'Minimal User'
        }
        response = client.post(
            '/api/auth/register',
            data=json.dumps(minimal_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_register_missing_username_fails(self, client, sample_user_data):
        """TC3: Missing username should fail"""
        data = sample_user_data.copy()
        del data['username']
        
        response = client.post(
            '/api/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'username' in data['error'].lower()
    
    def test_register_missing_email_fails(self, client, sample_user_data):
        """TC4: Missing email should fail"""
        data = sample_user_data.copy()
        del data['email']
        
        response = client.post(
            '/api/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'email' in data['error'].lower()
    
    def test_register_missing_password_fails(self, client, sample_user_data):
        """TC5: Missing password should fail"""
        data = sample_user_data.copy()
        del data['password']
        
        response = client.post(
            '/api/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'password' in data['error'].lower()
    
    def test_register_missing_full_name_fails(self, client, sample_user_data):
        """TC6: Missing full_name should fail"""
        data = sample_user_data.copy()
        del data['full_name']
        
        response = client.post(
            '/api/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'full_name' in data['error'].lower()
    
    def test_register_empty_username_fails(self, client, sample_user_data):
        """TC7: Empty username should fail"""
        data = sample_user_data.copy()
        data['username'] = ''
        
        response = client.post(
            '/api/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_register_duplicate_username_fails(self, client, registered_user, sample_user_data):
        """TC8: Duplicate username should fail"""
        data = sample_user_data.copy()
        data['email'] = 'different@example.com'  # Different email but same username
        
        response = client.post(
            '/api/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'username' in data['error'].lower() or 'exists' in data['error'].lower()
    
    def test_register_duplicate_email_fails(self, client, registered_user, sample_user_data):
        """TC9: Duplicate email should fail"""
        data = sample_user_data.copy()
        data['username'] = 'differentuser'  # Different username but same email
        
        response = client.post(
            '/api/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'email' in data['error'].lower() or 'exists' in data['error'].lower()
    
    def test_register_invalid_email_format_fails(self, client, sample_user_data):
        """TC10: Invalid email format should fail"""
        data = sample_user_data.copy()
        data['email'] = 'invalid-email'
        
        response = client.post(
            '/api/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_register_invalid_phone_format_fails(self, client, sample_user_data):
        """TC11: Invalid phone format should fail"""
        data = sample_user_data.copy()
        data['phone_number'] = '123'  # Too short
        
        response = client.post(
            '/api/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_register_password_is_hashed(self, client, sample_user_data, clean_db):
        """TC12: Password should be hashed, not stored as plain text"""
        response = client.post(
            '/api/auth/register',
            data=json.dumps(sample_user_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        user_id = data['user_id']
        
        # Verify password is hashed in database (using same DB as API)
        from app.infrastructure.database.models.user_model import UserModel
        user_model = clean_db.query(UserModel).filter_by(user_id=user_id).first()
        assert user_model is not None
        assert user_model.password_hash != sample_user_data['password']
        assert user_model.password_hash.startswith('$2b$')  # bcrypt hash
    
    def test_register_no_json_body_fails(self, client):
        """TC13: Request without JSON body should fail"""
        response = client.post('/api/auth/register')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_register_invalid_json_fails(self, client):
        """TC14: Invalid JSON should fail"""
        response = client.post(
            '/api/auth/register',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code in [400, 500]


class TestLoginEndpoint:
    """Test POST /api/auth/login"""
    
    def test_login_with_username_success(self, client, registered_user):
        """TC1: Login with username should succeed"""
        response = client.post(
            '/api/auth/login',
            data=json.dumps({
                'username': registered_user['username'],
                'password': registered_user['password']
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'user' in data
        assert data['user']['username'] == registered_user['username']
        assert data['user']['role'] == 'CUSTOMER'
    
    def test_login_with_email_success(self, client, registered_user):
        """TC2: Login with email should succeed"""
        response = client.post(
            '/api/auth/login',
            data=json.dumps({
                'username': registered_user['email'],  # Using email as username
                'password': registered_user['password']
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['user']['email'] == registered_user['email']
    
    def test_login_sets_session_cookie(self, client, registered_user):
        """TC3: Login should set session cookie"""
        with client:
            response = client.post(
                '/api/auth/login',
                data=json.dumps({
                    'username': registered_user['username'],
                    'password': registered_user['password']
                }),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            # Check session is set
            with client.session_transaction() as sess:
                assert 'user_id' in sess
                assert sess['user_id'] == registered_user['user_id']
                assert 'username' in sess
                assert 'role' in sess
    
    def test_login_wrong_password_fails(self, client, registered_user):
        """TC4: Login with wrong password should fail"""
        response = client.post(
            '/api/auth/login',
            data=json.dumps({
                'username': registered_user['username'],
                'password': 'WrongPassword123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'invalid' in data['error'].lower() or 'password' in data['error'].lower()
    
    def test_login_nonexistent_username_fails(self, client):
        """TC5: Login with nonexistent username should fail"""
        response = client.post(
            '/api/auth/login',
            data=json.dumps({
                'username': 'nonexistentuser',
                'password': 'SomePassword123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_login_nonexistent_email_fails(self, client):
        """TC6: Login with nonexistent email should fail"""
        response = client.post(
            '/api/auth/login',
            data=json.dumps({
                'username': 'nonexistent@example.com',
                'password': 'SomePassword123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_login_missing_username_fails(self, client):
        """TC7: Login without username should fail"""
        response = client.post(
            '/api/auth/login',
            data=json.dumps({'password': 'SomePassword123'}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_login_missing_password_fails(self, client):
        """TC8: Login without password should fail"""
        response = client.post(
            '/api/auth/login',
            data=json.dumps({'username': 'testuser'}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_login_empty_credentials_fails(self, client):
        """TC9: Login with empty credentials should fail"""
        response = client.post(
            '/api/auth/login',
            data=json.dumps({'username': '', 'password': ''}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_login_case_sensitive_username(self, client, registered_user):
        """TC10: Username should be case-sensitive"""
        response = client.post(
            '/api/auth/login',
            data=json.dumps({
                'username': registered_user['username'].upper(),
                'password': registered_user['password']
            }),
            content_type='application/json'
        )
        
        # This should fail because username is case-sensitive
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False


class TestLogoutEndpoint:
    """Test POST /api/auth/logout"""
    
    def test_logout_clears_session(self, client, registered_user):
        """TC1: Logout should clear session"""
        # First login
        client.post(
            '/api/auth/login',
            data=json.dumps({
                'username': registered_user['username'],
                'password': registered_user['password']
            }),
            content_type='application/json'
        )
        
        # Then logout
        with client:
            response = client.post('/api/auth/logout')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'logged out' in data['message'].lower()
            
            # Check session is cleared
            with client.session_transaction() as sess:
                assert 'user_id' not in sess
    
    def test_logout_without_login_succeeds(self, client):
        """TC2: Logout without being logged in should succeed"""
        response = client.post('/api/auth/logout')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True


class TestGetCurrentUserEndpoint:
    """Test GET /api/auth/me"""
    
    def test_get_current_user_when_logged_in(self, client, registered_user):
        """TC1: Get current user when logged in should succeed"""
        # First login
        client.post(
            '/api/auth/login',
            data=json.dumps({
                'username': registered_user['username'],
                'password': registered_user['password']
            }),
            content_type='application/json'
        )
        
        # Then get current user
        response = client.get('/api/auth/me')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'user' in data
        assert data['user']['username'] == registered_user['username']
        assert data['user']['email'] == registered_user['email']
        assert data['user']['full_name'] == registered_user['full_name']
        assert data['user']['role'] == 'CUSTOMER'
        assert data['user']['is_active'] is True
        # Password hash should not be exposed
        assert 'password' not in data['user']
        assert 'password_hash' not in data['user']
    
    def test_get_current_user_when_not_logged_in(self, client):
        """TC2: Get current user when not logged in should fail"""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'not authenticated' in data['error'].lower()
    
    def test_get_current_user_after_logout(self, client, registered_user):
        """TC3: Get current user after logout should fail"""
        # Login
        client.post(
            '/api/auth/login',
            data=json.dumps({
                'username': registered_user['username'],
                'password': registered_user['password']
            }),
            content_type='application/json'
        )
        
        # Logout
        client.post('/api/auth/logout')
        
        # Try to get current user
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False


class TestAuthenticationFlow:
    """Test complete authentication flow"""
    
    def test_complete_auth_flow(self, client, sample_user_data):
        """TC1: Complete flow - Register → Login → Get user → Logout"""
        # Step 1: Register
        response = client.post(
            '/api/auth/register',
            data=json.dumps(sample_user_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        
        # Step 2: Login
        response = client.post(
            '/api/auth/login',
            data=json.dumps({
                'username': sample_user_data['username'],
                'password': sample_user_data['password']
            }),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Step 3: Get current user
        response = client.get('/api/auth/me')
        assert response.status_code == 200
        
        # Step 4: Logout
        response = client.post('/api/auth/logout')
        assert response.status_code == 200
        
        # Step 5: Verify cannot access protected resource
        response = client.get('/api/auth/me')
        assert response.status_code == 401
    
    def test_multiple_login_sessions(self, client, registered_user):
        """TC2: Multiple login attempts should update session"""
        # Login first time
        response1 = client.post(
            '/api/auth/login',
            data=json.dumps({
                'username': registered_user['username'],
                'password': registered_user['password']
            }),
            content_type='application/json'
        )
        assert response1.status_code == 200
        
        # Login again (should succeed)
        response2 = client.post(
            '/api/auth/login',
            data=json.dumps({
                'username': registered_user['username'],
                'password': registered_user['password']
            }),
            content_type='application/json'
        )
        assert response2.status_code == 200
        
        # Should still be able to access protected resource
        response3 = client.get('/api/auth/me')
        assert response3.status_code == 200
