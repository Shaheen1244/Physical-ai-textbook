import asyncio
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from vector_db import vector_db

load_dotenv()

class DocumentProcessor:
    def __init__(self, collection_name: str = "book"):
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.collection_name = collection_name

    def process_document(self, content: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Process a document by splitting it into chunks and preparing for embedding
        """
        # Split the document into chunks
        chunks = self.text_splitter.split_text(content)

        # Prepare chunks with metadata
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata or {}
            chunk_metadata["chunk_index"] = i
            chunk_metadata["total_chunks"] = len(chunks)
            # Ensure collection name is in metadata
            chunk_metadata["collection"] = self.collection_name

            processed_chunks.append({
                "content": chunk,
                "metadata": chunk_metadata
            })

        return processed_chunks

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a text using OpenAI
        """
        embedding = self.embeddings.embed_query(text)
        return embedding

    def add_document_to_vector_db(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """
        Process a document and add it to the vector database
        """
        # Process the document into chunks
        chunks = self.process_document(content, metadata)

        # Add each chunk to the vector database
        doc_ids = []
        for chunk in chunks:
            # Generate embedding for the chunk
            embedding = self.embed_text(chunk["content"])

            # Add to vector database with collection name
            doc_id = vector_db.add_document(
                content=chunk["content"],
                metadata=chunk["metadata"],
                collection_name=self.collection_name
            )
            doc_ids.append(doc_id)

        # Return the first document ID as the main ID
        return doc_ids[0] if doc_ids else None

    def search_documents(self, query: str, limit: int = 5, collection_name: str = None) -> List[Dict[str, Any]]:
        """
        Search for relevant documents based on a query
        """
        # Use provided collection name or default to instance collection name
        target_collection = collection_name or self.collection_name

        # Generate embedding for the query
        query_embedding = self.embed_text(query)

        # Search in vector database with specific collection
        results = vector_db.search(query_embedding, limit=limit, collection_name=target_collection)

        return results

# Global instance
document_processor = DocumentProcessor()