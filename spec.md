# Feature Specification: RAG Qdrant Integration

**Feature Branch**: `1-rag-qdrant`
**Created**: 2026-01-06
**Status**: Draft
**Input**: User description: "You are a senior AI engineer.

Task:
- Read all book markdown files in /docs
- Create embeddings for each section/chapter
- Store them in Qdrant collection named \"book\"
- Setup RAG API endpoint:
   - Input: user question
   - Output: answer using only book content
- Do not modify the book markdown files
- Provide code for:
   - Qdrant indexing
   - API route to serve answers to chatbot
   - Frontend integration with ChatbotWidget
- Ensure everything is ready for localhost testing
You are a senior AI engineer.

Task:
- Read all book markdown files in /docs
- Create embeddings for each section/chapter
- Store them in Qdrant collection named \"book\"
- Setup RAG API endpoint:
   - Input: user question
   - Output: answer using only book content
- Do not modify the book markdown files
- Provide code for:
   - Qdrant indexing
   - API route to serve answers to chatbot
   - Frontend integration with ChatbotWidget
- Ensure everything is ready for localhost testing"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Query Book Content via Chatbot (Priority: P1)

A user wants to ask questions about the book content and receive accurate answers based on the book's information. The user interacts with a chatbot widget on the website that understands the book content and can provide relevant responses.

**Why this priority**: This is the core value proposition of the feature - allowing users to interact with book content through natural language queries.

**Independent Test**: User can ask a question in the chatbot interface and receive a relevant answer that is based on the book content, demonstrating the RAG functionality.

**Acceptance Scenarios**:

1. **Given** the user is on a page with the chatbot widget, **When** the user types a question related to book content and submits it, **Then** the system returns an answer based on the book content within 5 seconds
2. **Given** the user asks a question that has no relevant content in the book, **When** the user submits the question, **Then** the system responds with "I couldn't find relevant information in the book about that topic"

---

### User Story 2 - Index Book Content (Priority: P1)

An administrator or system needs to process all book markdown files in the /docs directory, extract sections/chapters, create embeddings, and store them in a Qdrant vector database for retrieval.

**Why this priority**: Without proper indexing, the RAG system cannot function, making this a prerequisite for the core functionality.

**Independent Test**: The system can read all markdown files in /docs, process them into chunks, generate embeddings, and store them in a Qdrant collection named "book".

**Acceptance Scenarios**:

1. **Given** book markdown files exist in the /docs directory, **When** the indexing process runs, **Then** all content is processed into appropriate chunks and stored in the "book" Qdrant collection
2. **Given** the indexing process has completed, **When** checking the Qdrant collection, **Then** the "book" collection contains all book content as vector embeddings with associated metadata

---

### User Story 3 - Integrate with Existing Chatbot Widget (Priority: P2)

The RAG functionality should be seamlessly integrated with the existing ChatbotWidget component, allowing users to access book-specific answers without changing the user interface significantly.

**Why this priority**: This ensures the feature integrates well with existing UI components and provides a familiar experience for users.

**Independent Test**: The existing ChatbotWidget can be configured to use the RAG backend instead of its current response mechanism when querying about book content.

**Acceptance Scenarios**:

1. **Given** the ChatbotWidget is configured for book queries, **When** a user submits a question, **Then** the response comes from the RAG system using book content

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST read all markdown files from the /docs directory
- **FR-002**: System MUST parse markdown files into logical sections/chapters for processing
- **FR-003**: System MUST generate embeddings for each content chunk using an appropriate embedding model
- **FR-004**: System MUST store embeddings in a Qdrant collection named "book" with proper metadata
- **FR-005**: System MUST provide an API endpoint that accepts user questions and returns answers based on book content
- **FR-006**: System MUST implement similarity search to find relevant book content for user questions
- **FR-007**: System MUST generate answers that are grounded in the retrieved book content
- **FR-008**: System MUST integrate with the existing ChatbotWidget component
- **FR-009**: System MUST handle cases where no relevant content is found in the book
- **FR-010**: System MUST preserve original book markdown files without modification

### Key Entities *(include if feature involves data)*

- **BookContentChunk**: Represents a section of book content that has been processed and embedded, including the original text, embedding vector, and metadata (source file, section, etc.)
- **QdrantCollection**: A vector database collection named "book" that stores content chunks with their embeddings for similarity search
- **UserQuery**: A question submitted by a user that needs to be answered using book content
- **RAGResponse**: An answer generated by the system based on retrieved book content

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can ask questions about book content and receive relevant answers within 5 seconds
- **SC-002**: The system successfully indexes all book markdown files in the /docs directory without errors
- **SC-003**: The RAG system achieves at least 80% accuracy in retrieving relevant book content for sample questions
- **SC-004**: The ChatbotWidget successfully integrates with the RAG backend and provides book-specific answers
- **SC-005**: The system is fully functional and testable on localhost environment
- **SC-006**: All book markdown files remain unmodified after the indexing process