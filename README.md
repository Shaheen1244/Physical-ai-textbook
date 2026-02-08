# Physical AI RAG Chatbot API

This is a comprehensive RAG (Retrieval-Augmented Generation) chatbot API designed for the Physical AI textbook project. It integrates multiple technologies including FastAPI, Qdrant vector database, PostgreSQL, OpenAI, and Claude Code agents.

## Features

- **RAG-based Chatbot**: Uses document retrieval to provide accurate responses based on provided content
- **User Authentication**: Secure JWT-based authentication system
- **Document Management**: Upload, store, and retrieve documents in a vector database
- **Claude Code Agents**: Task execution with specialized skills
- **Personalization**: User-specific content adaptation and preferences
- **Full CRUD Operations**: Complete management of user data and documents

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │◄──►│   FastAPI API    │◄──►│  PostgreSQL     │
│ (Docusaurus)    │    │  (Authentication │    │  (User Data)    │
└─────────────────┘    │   & Routing)     │    └─────────────────┘
                       └──────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   Qdrant Vector   │
                    │   Database        │
                    │  (Documents &     │
                    │   Embeddings)     │
                    └───────────────────┘
```

## Technologies Used

- **FastAPI**: Web framework for API development
- **Qdrant**: Vector database for document storage and similarity search
- **PostgreSQL**: Relational database for user management
- **OpenAI API**: For embeddings and language model capabilities
- **LangChain**: For RAG pipeline implementation
- **SQLAlchemy**: For database ORM
- **PyJWT**: For authentication tokens
- **PassLib**: For password hashing

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token

### Chat
- `POST /chat` - Main chat endpoint with RAG capabilities

### Documents
- `POST /documents/upload` - Upload a document for RAG system
- `GET /documents` - List user's documents
- `DELETE /documents/{doc_id}` - Delete a document

### Claude Code Agents
- `POST /agents/execute` - Execute a task with Claude Code agent
- `GET /agents/skills` - List available agent skills
- `POST /agents/skills/execute` - Execute a specific skill

### Personalization
- `GET /personalization/profile` - Get user profile
- `GET /personalization/preferences` - Get user preferences
- `PUT /personalization/preferences` - Update user preferences

### System
- `GET /` - Health check and root endpoint
- `GET /health` - Health check

## Environment Variables

Create a `.env` file in the api directory with the following variables:

```bash
OPENAI_API_KEY=your_openai_api_key_here
QDRANT_URL=http://localhost:6333  # or your Qdrant Cloud URL
QDRANT_API_KEY=your_qdrant_api_key  # if using Qdrant Cloud
DATABASE_URL=postgresql://username:password@localhost/dbname
SECRET_KEY=your_secret_key_for_jwt_tokens
```

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (see above)

3. Initialize the database:
```bash
python init_db.py
```

4. Start the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Running Tests

To run integration tests:
```bash
python test_integration.py
```

Note: Make sure the API server is running before executing the tests.

## How It Works

1. **Document Processing**: Documents are uploaded and processed into chunks with embeddings
2. **Vector Storage**: Chunks are stored in Qdrant vector database for fast similarity search
3. **Query Processing**: User queries are embedded and searched against document vectors
4. **RAG Generation**: Relevant documents are used to generate context-aware responses
5. **Personalization**: Responses are tailored based on user preferences and history
6. **Agent Tasks**: Complex tasks are handled by Claude Code agents with specialized skills

## Security

- Passwords are securely hashed using bcrypt
- JWT tokens are used for authentication
- All endpoints requiring authentication are protected
- SQL injection is prevented through ORM usage
- Input validation is enforced through Pydantic models

## Scalability

The system is designed to scale:
- Qdrant handles vector search efficiently
- PostgreSQL can be scaled with proper indexing
- FastAPI provides async capabilities
- Authentication system supports concurrent users