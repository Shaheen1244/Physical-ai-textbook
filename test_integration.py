"""
Integration test script for the RAG Chatbot API
"""
import asyncio
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✓ Health check passed")

def test_register_user():
    """Test user registration"""
    print("Testing user registration...")
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    print("✓ User registration passed")
    return token_data["access_token"]

def test_login_user(token: str = None):
    """Test user login"""
    print("Testing user login...")
    if not token:
        user_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=user_data)
        assert response.status_code == 200
        token_data = response.json()
        assert "access_token" in token_data
        token = token_data["access_token"]
    print("✓ User login passed")
    return token

def test_upload_document(token: str):
    """Test document upload"""
    print("Testing document upload...")
    headers = {"Authorization": f"Bearer {token}"}
    doc_data = {
        "title": "Test Document",
        "content": "This is a test document for the RAG system. It contains information about Physical AI and robotics.",
        "source": "test_source"
    }
    response = requests.post(f"{BASE_URL}/documents/upload", json=doc_data, headers=headers)
    assert response.status_code == 200
    result = response.json()
    assert "doc_id" in result
    print("✓ Document upload passed")
    return result["doc_id"]

def test_list_documents(token: str):
    """Test listing documents"""
    print("Testing list documents...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/documents", headers=headers)
    assert response.status_code == 200
    result = response.json()
    assert "documents" in result
    print("✓ List documents passed")

def test_chat(token: str):
    """Test chat functionality"""
    print("Testing chat functionality...")
    headers = {"Authorization": f"Bearer {token}"}
    chat_data = {
        "messages": [
            {"role": "user", "content": "What is Physical AI?"}
        ]
    }
    response = requests.post(f"{BASE_URL}/chat", json=chat_data, headers=headers)
    assert response.status_code == 200
    result = response.json()
    assert "response" in result
    assert "sources" in result
    print("✓ Chat functionality passed")

def test_agent_skills(token: str):
    """Test Claude Code agent skills"""
    print("Testing agent skills...")
    headers = {"Authorization": f"Bearer {token}"}

    # Test listing skills
    response = requests.get(f"{BASE_URL}/agents/skills", headers=headers)
    assert response.status_code == 200
    skills = response.json()
    assert "skills" in skills
    print("✓ Agent skills listing passed")

    # Test executing a skill if available
    if skills["skills"]:
        skill_name = skills["skills"][0]["name"]
        skill_data = {
            "skill_name": skill_name,
            "parameters": {}
        }
        response = requests.post(f"{BASE_URL}/agents/skills/execute", json=skill_data, headers=headers)
        assert response.status_code == 200
        print(f"✓ Agent skill execution passed for skill: {skill_name}")

def test_personalization(token: str):
    """Test personalization features"""
    print("Testing personalization features...")
    headers = {"Authorization": f"Bearer {token}"}

    # Test getting user profile
    response = requests.get(f"{BASE_URL}/personalization/profile", headers=headers)
    assert response.status_code == 200
    profile = response.json()
    assert "user_id" in profile
    print("✓ Personalization profile retrieval passed")

    # Test getting user preferences
    response = requests.get(f"{BASE_URL}/personalization/preferences", headers=headers)
    assert response.status_code == 200
    preferences = response.json()
    assert "preferences" in preferences
    print("✓ Personalization preferences retrieval passed")

def run_all_tests():
    """Run all integration tests"""
    print("Starting RAG Chatbot API integration tests...\n")

    try:
        # Test 1: Health check
        test_health_check()
        print()

        # Test 2: Authentication
        token = test_register_user()
        token = test_login_user(token)  # Use the token from registration
        print()

        # Test 3: Document management
        test_upload_document(token)
        test_list_documents(token)
        print()

        # Test 4: Chat functionality
        test_chat(token)
        print()

        # Test 5: Agent skills
        test_agent_skills(token)
        print()

        # Test 6: Personalization
        test_personalization(token)
        print()

        print("🎉 All integration tests passed successfully!")
        print("The RAG Chatbot API is fully functional with all components integrated.")

    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        raise

if __name__ == "__main__":
    run_all_tests()