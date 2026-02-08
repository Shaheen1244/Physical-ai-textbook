from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv
from rag_chain import rag_chain
from document_processor import document_processor
from vector_db import vector_db
from auth import get_current_user, register_user, authenticate_user, create_access_token, github_login, GitHubLoginRequest, UserCreate, UserLogin, Token
from database import SessionLocal, get_db, UserProfile
from sqlalchemy.orm import Session
from agents import claude_agent, skill_manager
from personalization import personalization_engine, UserPreference

# Load environment variables
load_dotenv()

# Validate required environment variables
required_env_vars = ["OPENAI_API_KEY"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    print(f"Warning: Missing required environment variables: {', '.join(missing_vars)}")

# Initialize FastAPI app
app = FastAPI(
    title="Physical AI RAG Chatbot API",
    description="API for RAG-based chatbot for Physical AI textbook",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event():
    """
    Startup event to ensure Qdrant collection exists
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        from vector_db import vector_db
        # Access the book collection to ensure it's initialized
        # The VectorDB class constructor already handles collection creation
        logger.info("Qdrant collection verification completed on startup")
    except Exception as e:
        logger.error(f"Error during startup verification of Qdrant collection: {str(e)}")
        # Don't raise the exception as it would prevent the server from starting
        # The system should be resilient to temporary Qdrant connection issues

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: List[dict] = []

class DocumentUpload(BaseModel):
    title: str
    content: str
    source: Optional[str] = None

class AgentTaskRequest(BaseModel):
    task: str
    user_id: Optional[str] = None

class AgentTaskResponse(BaseModel):
    result: str
    status: str

class UserBackground(BaseModel):
    education_level: str = "undergraduate"  # high_school, undergraduate, graduate, phd, professional
    field_of_study: str = "general"  # general, computer_science, robotics, engineering, physics, math
    experience_level: str = "beginner"  # beginner, intermediate, advanced, expert
    native_language: str = "english"  # english, urdu, etc.
    preferred_language: str = "english"  # language for content delivery
    learning_goals: List[str] = []
    special_needs: List[str] = []  # visual, hearing, cognitive, etc.

class UserPreference(BaseModel):
    learning_style: str = "comprehensive"  # comprehensive, concise, example-focused
    difficulty_level: str = "intermediate"  # beginner, intermediate, advanced
    preferred_topics: List[str] = []
    notification_preferences: Dict[str, bool] = {"email": True, "push": False}
    content_format: str = "text"  # text, visual, audio, mixed
    background: UserBackground = UserBackground()

class SkillExecuteRequest(BaseModel):
    skill_name: str
    parameters: dict

# Authentication endpoints
@app.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    user = register_user(db, user_data)
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token
    """
    user = authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/github", response_model=Token)
async def github_auth(request: GitHubLoginRequest):
    """
    Authenticate user with GitHub OAuth and return access token
    """
    result = await github_login(request.code)
    return {"access_token": result["access_token"], "token_type": result["token_type"]}

@app.get("/auth/github/url")
async def get_github_auth_url():
    """
    Get GitHub OAuth authorization URL
    """
    client_id = os.getenv("GITHUB_CLIENT_ID")
    if not client_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GitHub OAuth not configured"
        )

    redirect_uri = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:3000/auth/github/callback")
    auth_url = f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=user:email"
    return {"auth_url": auth_url}

# Chat endpoints
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user = Depends(get_current_user)):
    """
    Main chat endpoint that handles conversation with RAG capabilities and personalization
    """
    # Get the last user message as the query
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    last_message = request.messages[-1]
    if last_message.role != "user":
        raise HTTPException(status_code=400, detail="Last message must be from user")

    # Generate response using RAG
    result = rag_chain.generate_response(last_message.content)

    # Personalize the response based on user preferences
    user_id = current_user.id
    personalized_response = await personalization_engine.personalize_content(result["response"], user_id)

    return ChatResponse(
        response=personalized_response,
        session_id=request.session_id or "default_session",
        sources=result["sources"]
    )


@app.post("/book-chat", response_model=ChatResponse)
async def book_chat(request: ChatRequest, current_user = Depends(get_current_user)):
    """
    Book-specific chat endpoint that handles queries only from book content
    """
    try:
        # Get the last user message as the query
        if not request.messages:
            raise HTTPException(status_code=400, detail="No messages provided")

        last_message = request.messages[-1]
        if last_message.role != "user":
            raise HTTPException(status_code=400, detail="Last message must be from user")

        # Log the incoming query
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Processing book chat request for user {current_user.id}, query: {last_message.content[:100]}...")

        # Generate response using book-specific RAG chain
        from rag_chain import RAGChain
        book_rag_chain = RAGChain(collection_name="book")
        result = book_rag_chain.generate_response(last_message.content)

        logger.info(f"Successfully processed book chat request, response length: {len(result['response'])}")
        return ChatResponse(
            response=result["response"],
            session_id=request.session_id or "default_session",
            sources=result.get("sources", [])
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the error with more details
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error processing book chat request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )


@app.post("/index-books")
async def index_books(current_user = Depends(get_current_user)):
    """
    Endpoint to trigger the indexing of all book content from /docs directory
    """
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Starting book indexing process for user {current_user.id}")

        from book_indexer import book_indexer
        result = book_indexer.index_books()

        logger.info(f"Book indexing completed: {result.get('message', 'Indexing finished')}")
        return result
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error during book indexing: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during indexing: {str(e)}"
        )


@app.get("/book-status")
async def book_status(current_user = Depends(get_current_user)):
    """
    Endpoint to check the status of book indexing
    """
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Checking book indexing status for user {current_user.id}")

        from book_indexer import book_indexer
        status = book_indexer.check_index_status()

        logger.info(f"Book status retrieved: indexed={status.get('indexed', False)}, count={status.get('document_count', 0)}")
        return status
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error checking book status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while checking book status: {str(e)}"
        )

@app.post("/documents/upload")
async def upload_document(doc_data: DocumentUpload, current_user = Depends(get_current_user)):
    """
    Endpoint to upload documents for RAG system
    """
    try:
        # Add document to vector database
        doc_id = document_processor.add_document_to_vector_db(
            doc_data.content,
            metadata={
                "title": doc_data.title,
                "source": doc_data.source,
                "user_id": current_user.id
            }
        )

        return {
            "message": "Document uploaded and processed successfully",
            "doc_id": doc_id,
            "title": doc_data.title
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.get("/documents")
async def list_documents(current_user = Depends(get_current_user)):
    """
    List all documents in the RAG system for the current user
    """
    try:
        documents = vector_db.list_documents()
        # Filter documents by user if needed
        user_documents = [
            {
                "id": doc["id"],
                "content": doc["content"][:100] + "..." if len(doc["content"]) > 100 else doc["content"],
                "metadata": doc["metadata"]
            }
            for doc in documents
            if doc["metadata"].get("user_id") == current_user.id
        ]
        return {"documents": user_documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")

@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, current_user = Depends(get_current_user)):
    """
    Delete a document from the RAG system
    """
    try:
        # In a real implementation, you would check if the user owns the document
        success = vector_db.delete_document(doc_id)
        if success:
            return {"message": f"Document {doc_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

# Claude Code Agent endpoints
@app.post("/agents/execute", response_model=AgentTaskResponse)
async def execute_agent_task(request: AgentTaskRequest, current_user = Depends(get_current_user)):
    """
    Execute a task using the Claude Code agent
    """
    try:
        # Use the current user's ID if not provided in the request
        user_id = request.user_id or current_user.id

        # Run the task using the Claude Code agent
        result = await claude_agent.run_task(request.task, str(user_id))

        return AgentTaskResponse(
            result=result["response"] if result["status"] == "success" else result["error"],
            status=result["status"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing agent task: {str(e)}")

@app.get("/agents/skills")
async def list_skills():
    """
    List all available skills for Claude Code agents
    """
    try:
        skills_list = []
        for name, skill in skill_manager.skills.items():
            skills_list.append({
                "name": name,
                "description": skill.description,
                "parameters": skill.parameters
            })
        return {"skills": skills_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving skills: {str(e)}")

@app.post("/agents/skills/execute")
async def execute_skill(request: SkillExecuteRequest, current_user = Depends(get_current_user)):
    """
    Execute a specific skill
    """
    try:
        result = skill_manager.execute_skill(request.skill_name, **request.parameters)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing skill: {str(e)}")

# Personalization endpoints
@app.get("/personalization/profile")
async def get_user_profile(current_user = Depends(get_current_user)):
    """
    Get user profile and personalization data
    """
    try:
        profile = await personalization_engine.get_user_profile(current_user.id)
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user profile: {str(e)}")

@app.get("/personalization/preferences")
async def get_user_preferences(current_user = Depends(get_current_user)):
    """
    Get user preferences
    """
    try:
        profile = await personalization_engine.get_user_profile(current_user.id)
        return {"preferences": profile["preferences"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user preferences: {str(e)}")

@app.put("/personalization/preferences")
async def update_user_preferences(preferences: UserPreference, current_user = Depends(get_current_user)):
    """
    Update user preferences
    """
    try:
        result = await personalization_engine.update_user_preferences(current_user.id, preferences)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user preferences: {str(e)}")

@app.get("/personalization/background")
async def get_user_background(current_user = Depends(get_current_user)):
    """
    Get user background information
    """
    try:
        profile = await personalization_engine.get_user_profile(current_user.id)
        return {"background": profile["background"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user background: {str(e)}")

@app.put("/personalization/background")
async def update_user_background(background: UserBackground, current_user = Depends(get_current_user)):
    """
    Update user background information
    """
    try:
        # Get current preferences to update only the background part
        profile = await personalization_engine.get_user_profile(current_user.id)
        current_preferences = profile["preferences"]

        # Update the background in the preferences
        updated_preferences = UserPreference(**current_preferences)
        updated_preferences.background = background

        result = await personalization_engine.update_user_preferences(current_user.id, updated_preferences)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user background: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Physical AI RAG Chatbot API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/book-health")
async def book_health_check():
    """
    Health check endpoint specifically for book RAG functionality
    """
    try:
        # Check if Qdrant is accessible
        from vector_db import vector_db
        # Try to list documents from the book collection as a basic check
        status = vector_db.list_documents(collection_name="book")

        return {
            "status": "healthy",
            "service": "book-rag",
            "details": {
                "qdrant_connection": True,
                "book_collection_accessible": True
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "book-rag",
            "details": {
                "qdrant_connection": False,
                "error": str(e)
            }
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)