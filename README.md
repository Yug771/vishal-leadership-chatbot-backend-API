# Leadership Chatbot

A secure and scalable chatbot application featuring a REST API using Python, Flask, and Docker. The application implements JWT-based authentication and maintains user-specific chat history using SQLite.

## Features

- JWT-based authentication
- RESTful API endpoints
- User-specific chat history
- Integration with LlamaCloudIndex for intelligent Q&A
- Swagger documentation
- Containerized with Docker and Docker Compose

## Swagger UI

![Swagger UI](\screenshot\Leadership-chatbot-api.png)

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- LlamaCloudIndex API credentials

## Getting Started

### Local Development

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd leadership-chatbot
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   # Edit .env to set your own values
   ```

4. Run the application:
   ```bash
   python run.py
   ```

5. Access the API documentation at http://localhost:5000/docs/

### Docker Deployment

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd leadership-chatbot
   ```

2. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   # Edit .env to set your own values
   ```

3. Build and run the Docker containers:
   ```bash
   docker-compose up -d
   ```

4. Access the API documentation at http://localhost/docs/

## API Endpoints

### Authentication

- `POST /api/signup`: Register a new user
- `POST /api/login`: Authenticate a user and get JWT tokens
- `POST /api/refresh`: Refresh an access token
- `GET /api/me`: Get information about the current user

### Chat

- `POST /api/ask-question`: Send a question to the chatbot
- `GET /api/chat-history`: Get chat history for the current user
- `GET /api/chat-history/<chat_id>`: Get a specific chat item

## Security Considerations

- Use HTTPS in production
- Store secrets in environment variables
- Implement proper password hashing
- Apply JWT best practices (short expiry, refresh tokens)
- Input sanitization to prevent XSS and SQL injection

## Production Deployment

For production deployment, consider:

1. Using a proper database (PostgreSQL, MySQL)
2. Setting up HTTPS with Let's Encrypt
3. Implementing monitoring and logging solutions
4. Setting up CI/CD pipelines
5. Configuring auto-scaling and load balancing

## Testing

Run tests with pytest:

```bash
pytest
```

## License

[MIT License](LICENSE) 