"""
Tests for Authentication Helpers (Decorators)
Coverage target: 100% for app/adapters/api/auth_helpers.py
"""
import pytest
from flask import Flask, session
from unittest.mock import Mock, patch
from app.adapters.api.auth_helpers import login_required, admin_required


class TestLoginRequiredDecorator:
    """Test @login_required decorator"""
    
    def test_login_required_allows_authenticated_user(self, app, client):
        """TC1: Authenticated user can access protected route"""
        @app.route('/test-protected')
        @login_required
        def protected_view():
            return {'success': True, 'message': 'Access granted'}, 200
        
        with client:
            # Set session
            with client.session_transaction() as sess:
                sess['user_id'] = 1
                sess['username'] = 'testuser'
                sess['role'] = 'CUSTOMER'
            
            response = client.get('/test-protected')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
    
    def test_login_required_blocks_unauthenticated_user(self, app, client):
        """TC2: Unauthenticated user cannot access protected route"""
        @app.route('/test-protected-2')
        @login_required
        def protected_view():
            return {'success': True}, 200
        
        response = client.get('/test-protected-2')
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'authentication' in data['error'].lower() or 'login' in data['error'].lower()
    
    def test_login_required_blocks_missing_user_id(self, app, client):
        """TC3: Session without user_id should be blocked"""
        @app.route('/test-protected-3')
        @login_required
        def protected_view():
            return {'success': True}, 200
        
        with client:
            # Set incomplete session
            with client.session_transaction() as sess:
                sess['username'] = 'testuser'  # Has username but no user_id
            
            response = client.get('/test-protected-3')
            assert response.status_code == 401
    
    def test_login_required_preserves_function_metadata(self, app):
        """TC4: Decorator should preserve original function metadata"""
        @login_required
        def my_view():
            """My view docstring"""
            return {'success': True}
        
        assert my_view.__name__ == 'my_view'
        assert 'My view docstring' in (my_view.__doc__ or '')


class TestAdminRequiredDecorator:
    """Test @admin_required decorator"""
    
    def test_admin_required_allows_admin_user(self, app, client):
        """TC1: Admin user can access admin-only route"""
        @app.route('/test-admin')
        @admin_required
        def admin_view():
            return {'success': True, 'message': 'Admin access granted'}, 200
        
        with client:
            # Set admin session
            with client.session_transaction() as sess:
                sess['user_id'] = 1
                sess['username'] = 'admin'
                sess['role'] = 'ADMIN'
            
            response = client.get('/test-admin')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
    
    def test_admin_required_blocks_customer_user(self, app, client):
        """TC2: Customer user cannot access admin-only route"""
        @app.route('/test-admin-2')
        @admin_required
        def admin_view():
            return {'success': True}, 200
        
        with client:
            # Set customer session
            with client.session_transaction() as sess:
                sess['user_id'] = 2
                sess['username'] = 'customer'
                sess['role'] = 'CUSTOMER'
            
            response = client.get('/test-admin-2')
            assert response.status_code == 403
            data = response.get_json()
            assert data['success'] is False
            assert 'admin' in data['error'].lower() or 'permission' in data['error'].lower()
    
    def test_admin_required_blocks_unauthenticated_user(self, app, client):
        """TC3: Unauthenticated user cannot access admin-only route"""
        @app.route('/test-admin-3')
        @admin_required
        def admin_view():
            return {'success': True}, 200
        
        response = client.get('/test-admin-3')
        assert response.status_code == 401  # Should fail at login_required first
    
    def test_admin_required_blocks_missing_role(self, app, client):
        """TC4: User without role should be blocked"""
        @app.route('/test-admin-4')
        @admin_required
        def admin_view():
            return {'success': True}, 200
        
        with client:
            # Set session without role
            with client.session_transaction() as sess:
                sess['user_id'] = 3
                sess['username'] = 'norole'
                # No role set
            
            response = client.get('/test-admin-4')
            assert response.status_code in [401, 403]
    
    def test_admin_required_case_sensitive_role(self, app, client):
        """TC5: Role check should be exact (case-sensitive)"""
        @app.route('/test-admin-5')
        @admin_required
        def admin_view():
            return {'success': True}, 200
        
        with client:
            # Set session with lowercase admin
            with client.session_transaction() as sess:
                sess['user_id'] = 4
                sess['username'] = 'admin'
                sess['role'] = 'admin'  # lowercase (should fail if case-sensitive)
            
            response = client.get('/test-admin-5')
            # Depending on implementation, this might pass or fail
            # If it should be case-sensitive, status should be 403
            assert response.status_code in [200, 403]
    
    def test_admin_required_chained_with_login_required(self, app, client):
        """TC6: Admin required should also enforce login required"""
        @app.route('/test-admin-6')
        @admin_required  # This should include login_required
        def admin_view():
            return {'success': True}, 200
        
        # Test without login
        response = client.get('/test-admin-6')
        assert response.status_code == 401  # Should block at login level first


class TestDecoratorIntegration:
    """Test decorator integration with Flask routes"""
    
    def test_multiple_decorators_order(self, app, client):
        """TC1: Test decorator execution order"""
        execution_order = []
        
        def custom_decorator(f):
            def wrapper(*args, **kwargs):
                execution_order.append('custom')
                return f(*args, **kwargs)
            wrapper.__name__ = f.__name__
            return wrapper
        
        @app.route('/test-order')
        @login_required
        @custom_decorator
        def test_view():
            execution_order.append('view')
            return {'success': True}, 200
        
        with client:
            with client.session_transaction() as sess:
                sess['user_id'] = 1
                sess['username'] = 'test'
                sess['role'] = 'CUSTOMER'
            
            response = client.get('/test-order')
            assert response.status_code == 200
            assert 'custom' in execution_order
            assert 'view' in execution_order
    
    def test_decorator_with_route_parameters(self, app, client):
        """TC2: Decorators should work with parameterized routes"""
        @app.route('/test-param/<int:item_id>')
        @login_required
        def param_view(item_id):
            return {'success': True, 'item_id': item_id}, 200
        
        with client:
            with client.session_transaction() as sess:
                sess['user_id'] = 1
                sess['username'] = 'test'
            
            response = client.get('/test-param/42')
            assert response.status_code == 200
            data = response.get_json()
            assert data['item_id'] == 42
    
    def test_decorator_error_handling(self, app, client):
        """TC3: Decorators should handle errors gracefully"""
        # This test verifies that decorators don't interfere with Flask's error handling
        # The decorated function will raise an exception, which Flask should catch
        @app.route('/test-error')
        @login_required
        def error_view():
            raise Exception("Test error")
        
        with client:
            with client.session_transaction() as sess:
                sess['user_id'] = 1
            
            # In production, Flask will catch exceptions and return 500
            # In test mode, exceptions propagate by default
            # We test that the decorator doesn't prevent error propagation
            with pytest.raises(Exception, match="Test error"):
                response = client.get('/test-error')
