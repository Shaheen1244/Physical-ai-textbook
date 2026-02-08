# Scripts Directory

This directory contains utility scripts for the Physical AI Textbook project.

## Available Scripts

### `indexBook.js`

Indexes all book content from the `/docs` directory into Qdrant vector database for RAG (Retrieval Augmented Generation) functionality.

#### Purpose
- Scans all markdown files inside the `/docs` directory
- Splits content into meaningful chunks (by heading/section)
- Generates embeddings for each chunk using OpenAI
- Creates or reuses Qdrant collection named "book"
- Upserts all embeddings into Qdrant
- Does NOT modify any markdown files

#### Usage
```bash
node scripts/indexBook.js
# or
npm run index-book
```

#### Prerequisites
- Ensure `.env.local` contains the required environment variables:
  - `QDRANT_URL`: The cloud Qdrant cluster URL
  - `QDRANT_API_KEY`: The API key for Qdrant cloud
  - `QDRANT_COLLECTION`: Collection name (defaults to "book")
  - `OPENAI_API_KEY`: Your OpenAI API key

#### Expected Output
The script will:
1. Scan and read all markdown files from the docs directory
2. Process each file and split into chunks
3. Generate embeddings for each chunk
4. Store the embeddings in the Qdrant collection
5. Provide progress updates and final statistics

#### Troubleshooting
- If you get connection errors, verify that:
  - Qdrant service is running and accessible
  - Network connectivity is available
  - URL and API key in `.env.local` are correct
  - Firewall is not blocking the connection