# Research: RAG Qdrant Integration

## Decision: Language Choice - Node.js vs Python
**Rationale**: Based on the existing project structure, this appears to be a Node.js/JavaScript project (Docusaurus-based). Using Node.js for consistency with the existing stack.
**Alternatives considered**: Python with FastAPI, which would offer better ML/AI library support but would introduce additional complexity with multiple runtimes.

## Decision: Embedding Model - OpenAI vs Local Model
**Rationale**: For simplicity and quality of embeddings, starting with OpenAI's embedding API. For production/local deployment, we can consider sentence-transformers or similar local models.
**Alternatives considered**:
- OpenAI embeddings API (text-embedding-ada-002) - chosen for simplicity and quality
- Local models (sentence-transformers/all-MiniLM-L6-v2) - for offline capability
- Hugging Face models - for variety of options

## Decision: Qdrant Integration Approach
**Rationale**: Using the official qdrant-client for Node.js to interact with Qdrant vector database.
**Alternatives considered**:
- Direct HTTP API calls - more complex but more control
- Official qdrant-client - chosen for ease of use and maintenance

## Decision: Markdown Processing
**Rationale**: Using existing markdown processing libraries to parse and chunk the book content appropriately.
**Alternatives considered**:
- remark/remark-parse - for parsing markdown to AST
- markdown-it - alternative markdown parser
- Custom parsing - for specific needs

## Decision: API Framework
**Rationale**: Using Express.js since it's the standard for Node.js APIs and fits well with the existing JavaScript ecosystem.
**Alternatives considered**:
- Express.js - chosen for simplicity and wide adoption
- Fastify - for performance
- Koa - for modern async/await support

## Decision: ChatbotWidget Integration
**Rationale**: Modifying the existing ChatbotWidget to use the new RAG API endpoint when specific conditions are met (e.g., book-related queries).
**Alternatives considered**:
- Creating a new component - would duplicate functionality
- Modifying existing ChatbotWidget - chosen for consistency