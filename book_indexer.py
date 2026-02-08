
"""
Book Indexer Module

This module handles the indexing of all markdown files in the /docs directory,
processing them into chunks with embeddings, and storing them in the Qdrant 'book' collection.
"""
import os
import glob
import asyncio
from typing import List, Dict, Any
from pathlib import Path
import markdown
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import logging

from .vector_db import vector_db
from .document_processor import document_processor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BookIndexer:
    """
    Handles indexing of all book markdown files in the /docs directory
    """

    def __init__(self, collection_name: str = "book"):
        """
        Initialize the BookIndexer with a specific collection name
        """
        self.collection_name = collection_name
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def read_markdown_files(self, docs_path: str = "docs/") -> List[Dict[str, Any]]:
        """
        Read all markdown files from the docs directory
        """
        markdown_files = []

        # Find all markdown files in the docs directory and subdirectories
        for filepath in glob.glob(os.path.join(docs_path, "**/*.md"), recursive=True):
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()

                    # Extract the relative path from docs directory for metadata
                    relative_path = os.path.relpath(filepath, docs_path)

                    markdown_files.append({
                        "filename": os.path.basename(filepath),
                        "relative_path": relative_path,
                        "full_path": filepath,
                        "content": content
                    })

                logger.info(f"Read file: {filepath}")

            except Exception as e:
                logger.error(f"Error reading file {filepath}: {str(e)}")
                continue

        return markdown_files

    def chunk_markdown_content(self, filename: str, content: str) -> List[Dict[str, Any]]:
        """
        Split markdown content into chunks with proper metadata
        """
        # Simple splitting by headers might be better for book content
        # For now, using the text splitter
        chunks = self.text_splitter.split_text(content)

        chunked_content = []
        for i, chunk in enumerate(chunks):
            chunked_content.append({
                "content": chunk,
                "metadata": {
                    "source_file": filename,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "collection": self.collection_name
                }
            })

        return chunked_content

    def index_books(self, docs_path: str = "docs/") -> Dict[str, Any]:
        """
        Main method to index all book content from markdown files
        """
        logger.info(f"Starting to index books from {docs_path}")

        # Read all markdown files
        markdown_files = self.read_markdown_files(docs_path)

        if not markdown_files:
            logger.warning(f"No markdown files found in {docs_path}")
            return {
                "status": "no_files_found",
                "message": f"No markdown files found in {docs_path}",
                "indexed_files": 0,
                "total_chunks": 0
            }

        total_chunks = 0
        processed_files = 0

        # Process each file
        for file_info in markdown_files:
            logger.info(f"Processing {file_info['filename']}")

            # Chunk the content
            chunks = self.chunk_markdown_content(
                file_info["relative_path"],
                file_info["content"]
            )

            # Add each chunk to the vector database
            for chunk in chunks:
                try:
                    # Create a temporary document processor for the specific collection
                    from .document_processor import DocumentProcessor
                    temp_doc_processor = DocumentProcessor(collection_name=self.collection_name)

                    # Add to vector database using the document processor which handles embeddings
                    doc_id = temp_doc_processor.add_document_to_vector_db(
                        content=chunk["content"],
                        metadata=chunk["metadata"]
                    )

                    if doc_id:
                        total_chunks += 1

                except Exception as e:
                    logger.error(f"Error adding chunk to vector DB: {str(e)}")
                    continue

            processed_files += 1

        logger.info(f"Completed indexing: {processed_files} files, {total_chunks} chunks")

        return {
            "status": "completed",
            "message": f"Successfully indexed {processed_files} files with {total_chunks} chunks",
            "indexed_files": processed_files,
            "total_chunks": total_chunks,
            "collection_name": self.collection_name
        }

    def check_index_status(self) -> Dict[str, Any]:
        """
        Check the status of the book index
        """
        try:
            # Get count of documents in the book collection
            documents = vector_db.list_documents(collection_name=self.collection_name)

            return {
                "indexed": len(documents) > 0,
                "collection_name": self.collection_name,
                "document_count": len(documents),
                "last_indexed": None  # Would need to track this in a real implementation
            }
        except Exception as e:
            logger.error(f"Error checking index status: {str(e)}")
            return {
                "indexed": False,
                "collection_name": self.collection_name,
                "document_count": 0,
                "error": str(e)
            }


# Global instance
book_indexer = BookIndexer()