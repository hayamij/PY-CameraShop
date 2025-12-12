"""Test admin orders endpoint"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

# Create app
app = create_app()

with app.test_client() as client:
    # First login as admin
    login_response = client.post('/api/auth/login', json={
        'email': 'admin2@camerashop.com',
        'password': 'Admin123!@#'
    })
    
    print("Login Response:")
    print(login_response.status_code)
    print(login_response.get_json())
    print()
    
    # Test admin orders endpoint
    orders_response = client.get('/api/admin/orders?page=1&per_page=100')
    
    print("Orders Response:")
    print(orders_response.status_code)
    print(orders_response.get_json())
