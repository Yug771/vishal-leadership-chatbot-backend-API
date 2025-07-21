import json
import pytest
from unittest.mock import patch
from app import create_app, db
from app.models.user import User
from app.models.chat_history import ChatHistory

@pytest.fixture
def client():
    app = create_app('testing')
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@pytest.fixture
def auth_headers(client):
    """Create a user and get auth headers with JWT token."""
    # Register a user
    client.post(
        '/api/signup',
        data=json.dumps({
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test@123'
        }),
        content_type='application/json'
    )
    
    # Login to get tokens
    response = client.post(
        '/api/login',
        data=json.dumps({
            'username': 'testuser',
            'password': 'Test@123'
        }),
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    return {'Authorization': f'Bearer {data["access_token"]}'}

@patch('app.services.llama_service.LlamaService.get_response')
def test_ask_question(mock_get_response, client, auth_headers):
    """Test asking a question to the chatbot."""
    mock_get_response.return_value = "This is a test response from the leadership chatbot."
    
    response = client.post(
        '/api/ask-question',
        data=json.dumps({
            'question': 'What makes a good leader?'
        }),
        content_type='application/json',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['question'] == 'What makes a good leader?'
    assert data['response'] == "This is a test response from the leadership chatbot."
    assert 'chat_id' in data
    
    # Verify that the chat history was saved to the database
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        chat = ChatHistory.query.filter_by(user_id=user.id).first()
        assert chat is not None
        assert chat.question == 'What makes a good leader?'
        assert chat.response == "This is a test response from the leadership chatbot."

def test_get_chat_history_empty(client, auth_headers):
    """Test getting empty chat history."""
    response = client.get(
        '/api/chat-history',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'chat_history' in data
    assert len(data['chat_history']) == 0
    assert data['total'] == 0

@patch('app.services.llama_service.LlamaService.get_response')
def test_get_chat_history(mock_get_response, client, auth_headers):
    """Test getting chat history after asking questions."""
    mock_get_response.return_value = "This is a test response."
    
    # Ask a question
    client.post(
        '/api/ask-question',
        data=json.dumps({
            'question': 'Question 1'
        }),
        content_type='application/json',
        headers=auth_headers
    )
    
    # Ask another question
    client.post(
        '/api/ask-question',
        data=json.dumps({
            'question': 'Question 2'
        }),
        content_type='application/json',
        headers=auth_headers
    )
    
    # Get chat history
    response = client.get(
        '/api/chat-history',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'chat_history' in data
    assert len(data['chat_history']) == 2
    assert data['total'] == 2
    
    # The most recent question should be first in the list (sorted by timestamp desc)
    assert data['chat_history'][0]['question'] == 'Question 2'
    assert data['chat_history'][1]['question'] == 'Question 1'

@patch('app.services.llama_service.LlamaService.get_response')
def test_get_specific_chat_item(mock_get_response, client, auth_headers):
    """Test getting a specific chat item."""
    mock_get_response.return_value = "This is a test response."
    
    # Ask a question
    response = client.post(
        '/api/ask-question',
        data=json.dumps({
            'question': 'Test question'
        }),
        content_type='application/json',
        headers=auth_headers
    )
    
    chat_id = json.loads(response.data)['chat_id']
    
    # Get specific chat item
    response = client.get(
        f'/api/chat-history/{chat_id}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'chat' in data
    assert data['chat']['id'] == chat_id
    assert data['chat']['question'] == 'Test question'
    assert data['chat']['response'] == 'This is a test response.' 