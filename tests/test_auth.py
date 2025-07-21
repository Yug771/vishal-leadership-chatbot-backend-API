import json
import pytest
from app import create_app, db
from app.models.user import User

@pytest.fixture
def client():
    app = create_app('testing')
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_signup(client):
    """Test user registration."""
    response = client.post(
        '/api/signup',
        data=json.dumps({
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test@123'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'user' in data
    assert data['user']['username'] == 'testuser'
    assert data['user']['email'] == 'test@example.com'

def test_signup_existing_username(client):
    """Test signup with an existing username."""
    # First create a user
    client.post(
        '/api/signup',
        data=json.dumps({
            'username': 'testuser',
            'email': 'test1@example.com',
            'password': 'Test@123'
        }),
        content_type='application/json'
    )
    
    # Try to create another user with the same username
    response = client.post(
        '/api/signup',
        data=json.dumps({
            'username': 'testuser',
            'email': 'test2@example.com',
            'password': 'Test@123'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 409
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Username already exists' in data['error']

def test_login(client):
    """Test user login."""
    # First create a user
    client.post(
        '/api/signup',
        data=json.dumps({
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test@123'
        }),
        content_type='application/json'
    )
    
    # Login with the created user
    response = client.post(
        '/api/login',
        data=json.dumps({
            'username': 'testuser',
            'password': 'Test@123'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert 'user' in data
    assert data['user']['username'] == 'testuser'
    
def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    # First create a user
    client.post(
        '/api/signup',
        data=json.dumps({
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test@123'
        }),
        content_type='application/json'
    )
    
    # Try to login with wrong password
    response = client.post(
        '/api/login',
        data=json.dumps({
            'username': 'testuser',
            'password': 'WrongPassword'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Invalid credentials' in data['error'] 