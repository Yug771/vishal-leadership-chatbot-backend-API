from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
from flasgger import swag_from
from app import db
from app.models.user import User
from app.models.chat_history import ChatHistory
from app.services.llama_service import get_llama_service
from app.utils.security import sanitize_input
from marshmallow import Schema, fields, ValidationError
import asyncio

chat_bp = Blueprint('chat', __name__)

class QuestionSchema(Schema):
    """Schema for validating question data."""
    question = fields.Str(required=True)

question_schema = QuestionSchema()

@chat_bp.route('/ask-question', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Chat'],
    'summary': 'Ask a question to the chatbot',
    'description': 'Send a question to the chatbot and get a response',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'question': {'type': 'string', 'example': 'What are the key qualities of good leadership?'}
                },
                'required': ['question']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Chatbot response',
            'schema': {
                'type': 'object',
                'properties': {
                    'question': {'type': 'string'},
                    'response': {'type': 'string'},
                    'chat_id': {'type': 'integer'}
                }
            }
        },
        400: {
            'description': 'Invalid request',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        401: {
            'description': 'Not authenticated',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def ask_question():
    """Ask a question to the chatbot."""
    data = request.get_json()
    
    # Validate input data
    try:
        validated_data = question_schema.load(data)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400
    
    # Get user ID from JWT token
    user_id = get_jwt_identity()
    
    # Ensure user exists
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Sanitize the question
    question = sanitize_input(validated_data['question'])
    
    # Get response from LlamaService
    llama_service = get_llama_service()
    
    # Create a new event loop and run the coroutine
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        response = loop.run_until_complete(llama_service.get_response(question))
    finally:
        loop.close()
    
    # Store the question and response in chat history
    chat_history = ChatHistory(
        user_id=user.id,
        question=question,
        response=response
    )
    db.session.add(chat_history)
    db.session.commit()
    
    return jsonify({
        'question': question,
        'response': response,
        'chat_id': chat_history.id
    }), 200

@chat_bp.route('/chat-history', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Chat'],
    'summary': 'Get user chat history',
    'description': 'Retrieve chat history for the authenticated user',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'limit',
            'in': 'query',
            'type': 'integer',
            'description': 'Maximum number of chat items to return',
            'default': 10
        },
        {
            'name': 'offset',
            'in': 'query',
            'type': 'integer',
            'description': 'Offset for pagination',
            'default': 0
        }
    ],
    'responses': {
        200: {
            'description': 'Chat history retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'chat_history': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'question': {'type': 'string'},
                                'response': {'type': 'string'},
                                'timestamp': {'type': 'string', 'format': 'date-time'}
                            }
                        }
                    },
                    'total': {'type': 'integer'},
                    'limit': {'type': 'integer'},
                    'offset': {'type': 'integer'}
                }
            }
        },
        401: {
            'description': 'Not authenticated',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def get_chat_history():
    """Get chat history for the current user."""
    user_id = get_jwt_identity()
    
    # Get pagination parameters
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Validate parameters
    if limit < 1 or limit > 100:
        limit = 10
    if offset < 0:
        offset = 0
    
    # Query for chat history
    chat_history = ChatHistory.query.filter_by(user_id=int(user_id))\
        .order_by(ChatHistory.timestamp.desc())\
        .limit(limit).offset(offset).all()
    
    # Get total count
    total = ChatHistory.query.filter_by(user_id=int(user_id)).count()
    
    return jsonify({
        'chat_history': [chat.to_dict() for chat in chat_history],
        'total': total,
        'limit': limit,
        'offset': offset
    }), 200

@chat_bp.route('/chat-history/<int:chat_id>', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Chat'],
    'summary': 'Get specific chat item',
    'description': 'Retrieve a specific chat item by ID',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'chat_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the chat item to retrieve'
        }
    ],
    'responses': {
        200: {
            'description': 'Chat item retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'chat': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'user_id': {'type': 'integer'},
                            'question': {'type': 'string'},
                            'response': {'type': 'string'},
                            'timestamp': {'type': 'string', 'format': 'date-time'}
                        }
                    }
                }
            }
        },
        401: {
            'description': 'Not authenticated',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        403: {
            'description': 'Forbidden - not owner of this chat item',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        404: {
            'description': 'Chat item not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def get_chat_item(chat_id):
    """Get a specific chat item by ID."""
    user_id = get_jwt_identity()
    
    # Find the chat item
    chat = ChatHistory.query.get(chat_id)
    
    if not chat:
        return jsonify({'error': 'Chat item not found'}), 404
    
    # Ensure user is the owner
    if chat.user_id != int(user_id):
        return jsonify({'error': 'You do not have permission to view this chat item'}), 403
    
    return jsonify({'chat': chat.to_dict()}), 200 