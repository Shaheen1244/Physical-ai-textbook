from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
from typing import List, Dict, Any
import uuid
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorDB:
    def __init__(self, collection_name: str = "documents"):
        # Initialize Qdrant client
        # If using local Qdrant: url="http://localhost:6333"
        # If using Qdrant Cloud: provide the URL and API key
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        qdrant_api_key = os.getenv("QDRANT_API_KEY", None)

        try:
            if qdrant_api_key:
                self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
            else:
                self.client = QdrantClient(url=qdrant_url)

            self.using_qdrant = True
            self.collection_name = collection_name
            self._create_collection()
        except Exception as e:
            logger.warning(f"Could not connect to Qdrant at {qdrant_url}: {str(e)}. Using in-memory fallback.")
            self.using_qdrant = False
            self.collection_name = collection_name
            self._documents = {}  # In-memory storage fallback

    def _create_collection(self):
        """
        Create a collection in Qdrant if it doesn't exist
        """
        try:
            # Check if collection exists
            self.client.get_collection(self.collection_name)
        except:
            # Create collection if it doesn't exist
            # Using 1536 dimensions for OpenAI embeddings
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )

    def add_document(self, content: str, metadata: Dict[str, Any] = None, doc_id: str = None, collection_name: str = None) -> str:
        """
        Add a document to the vector database
        """
        if doc_id is None:
            doc_id = str(uuid.uuid4())

        # Use provided collection name or default to instance collection name
        target_collection = collection_name or self.collection_name

        if self.using_qdrant:
            # In a real implementation, you would generate embeddings here
            # For now, using a placeholder embedding (this would be replaced with actual embedding logic)
            embedding = [0.0] * 1536  # Placeholder embedding

            self.client.upsert(
                collection_name=target_collection,
                points=[
                    models.PointStruct(
                        id=doc_id,
                        vector=embedding,
                        payload={
                            "content": content,
                            "metadata": metadata or {}
                        }
                    )
                ]
            )
        else:
            # In-memory storage fallback - using collection-specific storage
            collection_key = f"{target_collection}_documents"
            if not hasattr(self, collection_key):
                setattr(self, collection_key, {})

            collection_docs = getattr(self, collection_key)
            collection_docs[doc_id] = {
                "content": content,
                "metadata": metadata or {},
                "embedding": [0.0] * 1536  # Placeholder
            }

        return doc_id

    def search(self, query_embedding: List[float], limit: int = 5, collection_name: str = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents based on query embedding
        """
        # Use provided collection name or default to instance collection name
        target_collection = collection_name or self.collection_name

        if self.using_qdrant:
            results = self.client.search(
                collection_name=target_collection,
                query_vector=query_embedding,
                limit=limit
            )

            return [
                {
                    "id": result.id,
                    "content": result.payload.get("content", ""),
                    "metadata": result.payload.get("metadata", {}),
                    "score": result.score
                }
                for result in results
            ]
        else:
            # Simple in-memory search (cosine similarity would be better in a real implementation)
            collection_key = f"{target_collection}_documents"
            collection_docs = getattr(self, collection_key, {})

            results = []
            for doc_id, doc_data in collection_docs.items():
                # For fallback, just return all documents with a dummy score
                results.append({
                    "id": doc_id,
                    "content": doc_data["content"],
                    "metadata": doc_data["metadata"],
                    "score": 0.8  # Dummy score for fallback
                })

            # Sort by dummy score and return top results
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:limit]

    def delete_document(self, doc_id: str, collection_name: str = None) -> bool:
        """
        Delete a document by ID
        """
        # Use provided collection name or default to instance collection name
        target_collection = collection_name or self.collection_name

        if self.using_qdrant:
            try:
                self.client.delete(
                    collection_name=target_collection,
                    points_selector=models.PointIdsList(points=[doc_id])
                )
                return True
            except:
                return False
        else:
            # In-memory deletion
            collection_key = f"{target_collection}_documents"
            collection_docs = getattr(self, collection_key, {})

            if doc_id in collection_docs:
                del collection_docs[doc_id]
                # Update the attribute
                setattr(self, collection_key, collection_docs)
                return True
            return False

    def list_documents(self, collection_name: str = None) -> List[Dict[str, Any]]:
        """
        List all documents in the collection
        """
        # Use provided collection name or default to instance collection name
        target_collection = collection_name or self.collection_name

        if self.using_qdrant:
            results = self.client.scroll(
                collection_name=target_collection,
                limit=1000  # Adjust as needed
            )

            documents = []
            for point in results[0]:  # results is (points, next_page_offset)
                documents.append({
                    "id": point.id,
                    "content": point.payload.get("content", ""),
                    "metadata": point.payload.get("metadata", {})
                })

            return documents
        else:
            # In-memory list
            collection_key = f"{target_collection}_documents"
            collection_docs = getattr(self, collection_key, {})

            documents = []
            for doc_id, doc_data in collection_docs.items():
                documents.append({
                    "id": doc_id,
                    "content": doc_data["content"],
                    "metadata": doc_data["metadata"]
                })

            return documents

# Global instance - in production, you might want to handle this differently
vector_db = VectorDB(collection_name="book")