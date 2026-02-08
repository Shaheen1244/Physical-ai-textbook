# Implementation Tasks: RAG Qdrant Integration

**Feature**: RAG Qdrant Integration
**Branch**: `1-rag-qdrant`
**Spec**: `/specs/1-rag-qdrant/spec.md`
**Plan**: `/specs/1-rag-qdrant/plan.md`

## Phase 1: Setup Tasks

- [x] T001 Create book indexer module in `api/book_indexer.py`
- [x] T002 Update Qdrant vector database configuration to use "book" collection in `api/vector_db.py`
- [x] T003 Add required dependencies to `api/requirements.txt` for document processing

## Phase 2: Foundational Tasks

- [x] T004 [P] Update document processor to handle book-specific metadata in `api/document_processor.py`
- [x] T005 [P] Modify RAG chain to target book collection specifically in `api/rag_chain.py`
- [x] T006 [P] Update vector database to use "book" collection name in `api/vector_db.py`
- [x] T007 [P] Create configuration for similarity threshold and chunking in `api/config.py`

## Phase 3: User Story 1 - Query Book Content via Chatbot (P1)

- [x] T008 [US1] Create book-specific chat endpoint in `api/main.py`
- [x] T009 [US1] Update RAG chain to respond with "This topic is not covered in the book" when no content found in `api/rag_chain.py`
- [x] T010 [US1] Implement confidence scoring for book content retrieval in `api/rag_chain.py`
- [x] T011 [US1] Add error handling for book query endpoint in `api/main.py`
- [ ] T012 [US1] Create test for book query endpoint in `tests/integration/test_book_chat.py`

**Independent Test**: User can ask a question in the chatbot interface and receive a relevant answer that is based on the book content, demonstrating the RAG functionality.

**Acceptance Scenarios**:
1. Given the user is on a page with the chatbot widget, When the user types a question related to book content and submits it, Then the system returns an answer based on the book content within 5 seconds
2. Given the user asks a question that has no relevant content in the book, When the user submits the question, Then the system responds with "This topic is not covered in the book"

## Phase 4: User Story 2 - Index Book Content (P1)

- [x] T013 [US2] Create BookIndexer class in `api/book_indexer.py` to read all markdown files from /docs
- [x] T014 [US2] Implement markdown file reading and parsing logic in `api/book_indexer.py`
- [x] T015 [US2] Create chunking logic for book sections/chapters in `api/book_indexer.py`
- [x] T016 [US2] Implement embedding generation for book content chunks in `api/book_indexer.py`
- [x] T017 [US2] Store embeddings in Qdrant "book" collection with metadata in `api/book_indexer.py`
- [x] T018 [US2] Create indexing endpoint in `api/main.py`
- [x] T019 [US2] Add indexing status endpoint in `api/main.py`
- [ ] T020 [US2] Create test for book indexing functionality in `tests/integration/test_book_indexing.py`

**Independent Test**: The system can read all markdown files in /docs, process them into chunks, generate embeddings, and store them in a Qdrant collection named "book".

**Acceptance Scenarios**:
1. Given book markdown files exist in the /docs directory, When the indexing process runs, Then all content is processed into appropriate chunks and stored in the "book" Qdrant collection
2. Given the indexing process has completed, When checking the Qdrant collection, Then the "book" collection contains all book content as vector embeddings with associated metadata

## Phase 5: User Story 3 - Integrate with Existing Chatbot Widget (P2)

- [x] T021 [US3] Update ChatbotWidget to use book-specific endpoint in `src/components/ChatbotWidget.js`
- [x] T022 [US3] Update chatAPI utility to route to book-specific endpoint in `src/utils/chatAPI.js`
- [x] T023 [US3] Update welcome message in ChatbotWidget to reflect book-specific assistance in `src/components/ChatbotWidget.js`
- [x] T024 [US3] Ensure frontend does not access server-only variables in `src/components/ChatbotWidget.js`
- [ ] T025 [US3] Add frontend integration test in `tests/frontend/test_chatbot_integration.js`

**Independent Test**: The existing ChatbotWidget can be configured to use the RAG backend instead of its current response mechanism when querying about book content.

**Acceptance Scenarios**:
1. Given the ChatbotWidget is configured for book queries, When a user submits a question, Then the response comes from the RAG system using book content

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T026 Add environment variable validation for Qdrant and OpenAI settings in `api/main.py`
- [x] T027 Update .env.example with required environment variables for book RAG system
- [x] T028 Add health check endpoint for book RAG functionality in `api/main.py`
- [x] T029 Update documentation for book indexing and querying in `docs/book-rag-setup.md`
- [x] T030 Add error logging for book RAG operations in `api/main.py`
- [x] T031 Create startup script to ensure Qdrant collection exists before indexing in `api/main.py`

## Dependencies

- User Story 2 (Index Book Content) must be completed before User Story 1 (Query Book Content) can function
- Foundational tasks must be completed before any user story tasks

## Parallel Execution Examples

- Tasks T004, T005, T006, T007 can be executed in parallel as they modify different files
- Tasks T008, T009, T010, T011 can be executed in parallel as they're part of the same user story but different aspects
- Tasks T021, T022, T023, T024 can be executed in parallel as they're frontend changes

## Implementation Strategy

1. **MVP Scope**: Complete User Story 2 (Index Book Content) and User Story 1 (Query Book Content) to have basic functionality
2. **Incremental Delivery**:
   - First: Basic indexing and querying functionality
   - Second: Integration with existing chatbot widget
   - Third: Polish and additional features