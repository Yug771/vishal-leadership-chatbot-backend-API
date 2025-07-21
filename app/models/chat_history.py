from datetime import datetime
from app import db

class ChatHistory(db.Model):
    """Chat history model for storing user conversations."""
    __tablename__ = 'chat_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user_id, question, response):
        self.user_id = user_id
        self.question = question
        self.response = response
    
    def __repr__(self):
        return f'<ChatHistory {self.id}>'
    
    def to_dict(self):
        """Convert chat history object to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'question': self.question,
            'response': self.response,
            'timestamp': self.timestamp.isoformat()
        } 