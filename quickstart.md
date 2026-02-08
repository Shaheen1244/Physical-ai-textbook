# Quickstart: RAG Qdrant Integration

## Prerequisites

- Node.js 18+ installed
- Qdrant vector database running locally (or access to a Qdrant instance)
- OpenAI API key (or local embedding model configured)

## Setup

1. **Install dependencies:**
   ```bash
   npm install @qdrant/js-client-rest openai express remark remark-parse
   ```

2. **Set environment variables:**
   ```bash
   # For OpenAI embeddings
   export OPENAI_API_KEY=your_openai_api_key_here

   # For Qdrant connection
   export QDRANT_URL=http://localhost:6333
   ```

3. **Start Qdrant:**
   ```bash
   # Using Docker
   docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant

   # Or using the Qdrant CLI
   qdrant
   ```

## Index Book Content

1. **Run the indexing script:**
   ```bash
   node scripts/index-book-content.js
   ```

2. **Or use the API endpoint:**
   ```bash
   curl -X POST http://localhost:3000/api/rag/index
   ```

## Query Book Content

1. **Use the API endpoint:**
   ```bash
   curl -X POST http://localhost:3000/api/rag/query \
     -H "Content-Type: application/json" \
     -d '{"question": "What is the main concept discussed in chapter 1?"}'
   ```

## Integration with ChatbotWidget

1. **Configure the ChatbotWidget to use the RAG endpoint**
2. **Add logic to detect book-related queries**
3. **Route book-related queries to the RAG API**

## Running Locally

1. **Start the server:**
   ```bash
   npm run dev
   ```

2. **The API will be available at:**
   - `http://localhost:3000/api/rag/query` - for queries
   - `http://localhost:3000/api/rag/index` - for indexing