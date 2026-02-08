# RAG API Contract

## Endpoints

### POST /api/rag/query
**Description**: Submit a question and receive an answer based on book content

**Request:**
```json
{
  "question": "string (required) - The user's question about the book content",
  "context": "string (optional) - Additional context for the query"
}
```

**Response (200 OK):**
```json
{
  "id": "string - Unique identifier for the response",
  "question": "string - The original question",
  "answer": "string - The answer generated based on book content",
  "sourceChunks": [
    {
      "id": "string - ID of the source chunk",
      "content": "string - The content of the relevant chunk",
      "sourceFile": "string - The source file of the chunk",
      "sectionTitle": "string - The section title",
      "similarityScore": "number - How similar this chunk is to the query"
    }
  ],
  "confidenceScore": "number - Confidence level of the response (0-1)",
  "timestamp": "string - ISO date string of when response was generated"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "string - Error message explaining the issue",
  "code": "string - Error code"
}
```

**Response (500 Internal Server Error):**
```json
{
  "error": "string - Error message",
  "code": "string - Error code"
}
```

### POST /api/rag/index
**Description**: Index all book markdown files in /docs directory

**Request:**
```json
{
  "force": "boolean (optional) - Whether to force re-indexing if content already exists"
}
```

**Response (200 OK):**
```json
{
  "status": "string - Status of the indexing operation",
  "indexedFiles": "number - Number of files processed",
  "indexedChunks": "number - Number of content chunks created",
  "message": "string - Additional information about the operation"
}
```

**Response (500 Internal Server Error):**
```json
{
  "error": "string - Error message",
  "code": "string - Error code"
}
```

## Data Models

### QueryRequest
- question: string (required) - The user's question about the book content
- context: string (optional) - Additional context for the query

### QueryResponse
- id: string - Unique identifier for the response
- question: string - The original question
- answer: string - The answer generated based on book content
- sourceChunks: array of SourceChunk
- confidenceScore: number - Confidence level of the response (0-1)
- timestamp: string - ISO date string of when response was generated

### SourceChunk
- id: string - ID of the source chunk
- content: string - The content of the relevant chunk
- sourceFile: string - The source file of the chunk
- sectionTitle: string - The section title
- similarityScore: number - How similar this chunk is to the query

### IndexRequest
- force: boolean (optional) - Whether to force re-indexing if content already exists

### IndexResponse
- status: string - Status of the indexing operation
- indexedFiles: number - Number of files processed
- indexedChunks: number - Number of content chunks created
- message: string - Additional information about the operation