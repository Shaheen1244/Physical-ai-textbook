# Book RAG System Setup Guide

This guide explains how to set up and use the Book RAG (Retrieval Augmented Generation) system for querying book content.

## Prerequisites

- Python 3.8+
- Node.js (for frontend)
- Qdrant vector database (local or cloud)
- OpenAI API key

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
OPENAI_API_KEY=your-openai-api-key-here
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your-qdrant-api-key-here  # Optional for local, required for cloud
BOOK_COLLECTION_NAME=book
SIMILARITY_THRESHOLD=0.5
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## Setting up the Book Index

1. Place all book markdown files in the `/docs` directory
2. Run the indexing endpoint to process all files:

```bash
curl -X POST http://localhost:8000/index-books
```

## Using the Book Chat Interface

The system provides two endpoints:
- `/book-chat` - For book-specific queries
- `/chat` - For general queries (includes book content if relevant)

The frontend ChatbotWidget is configured to use the book-specific endpoint by default.

## API Endpoints

- `POST /index-books` - Index all markdown files in `/docs`
- `GET /book-status` - Check indexing status
- `POST /book-chat` - Query book content specifically
- `GET /book-health` - Health check for book RAG functionality

## Response Format

The API returns responses in the following format:

```json
{
  "response": "Answer to the question",
  "sources": [
    {
      "id": "document-id",
      "content": "Relevant content snippet...",
      "score": 0.85,
      "metadata": {
        "source_file": "chapter_3.md",
        "chunk_index": 2
      }
    }
  ]
}
```

## Troubleshooting

- If queries return "This topic is not covered in the book", the content is not in the indexed documents
- Ensure Qdrant is running and accessible
- Verify that your OpenAI API key is valid and has sufficient quota