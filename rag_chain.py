from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from document_processor import document_processor

load_dotenv()

class RAGChain:
    def __init__(self, collection_name: str = "book"):
        # Initialize the language model
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",  # You can change this to gpt-4 if preferred
            temperature=0.1,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        self.collection_name = collection_name

        # Define the prompt template for the RAG system
        self.template = """
        You are an AI assistant for the Physical AI textbook. Use the following context to answer the user's question.
        If the context doesn't contain enough information to answer the question, say "This topic is not covered in the book."
        Be concise and accurate in your response, and cite the sources when possible.

        Context:
        {context}

        Question: {question}

        Answer:
        """

        self.prompt = ChatPromptTemplate.from_template(self.template)

        # Create the RAG chain
        self.rag_chain = (
            {"context": self._retrieve_context, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def _retrieve_context(self, inputs: Dict[str, Any]) -> str:
        """
        Retrieve relevant context based on the question with confidence scoring
        """
        question = inputs["question"]

        # Search for relevant documents in the book collection
        results = document_processor.search_documents(question, limit=5, collection_name=self.collection_name)

        # Combine the content from relevant documents with confidence scoring
        context_parts = []
        for result in results:
            content = result["content"]
            score = result["score"]
            # Only include documents with a reasonable similarity score
            if score > 0.5:  # Adjust threshold as needed
                source = result.get('metadata', {}).get('source_file', result.get('metadata', {}).get('source', 'Unknown'))
                context_parts.append(f"Source: {source}\n{content}")

        return "\n\n".join(context_parts) if context_parts else "No relevant context found."

    def _calculate_confidence_score(self, results: List[Dict[str, Any]]) -> float:
        """
        Calculate an overall confidence score based on the retrieved results
        """
        if not results:
            return 0.0

        # Calculate average score of all results
        total_score = sum(result["score"] for result in results)
        avg_score = total_score / len(results)

        # Calculate max score among results
        max_score = max(result["score"] for result in results)

        # Combine average and max scores to determine confidence
        # Weight the max score higher to prioritize the best match
        confidence = (0.3 * avg_score) + (0.7 * max_score)

        return confidence

    def generate_response(self, question: str) -> Dict[str, Any]:
        """
        Generate a response to a question using the RAG chain with confidence scoring
        """
        try:
            # Search for sources first to calculate confidence
            search_results = document_processor.search_documents(question, limit=5, collection_name=self.collection_name)

            # Calculate confidence score based on search results
            confidence_score = self._calculate_confidence_score(search_results)

            # Check if confidence is too low (no relevant content found)
            if confidence_score < 0.3:  # Adjust threshold as needed
                return {
                    "response": "This topic is not covered in the book.",
                    "sources": []
                }

            # Generate response using the RAG chain
            response = self.rag_chain.invoke(question)

            # Check if the response indicates no content was found in the book
            if "This topic is not covered in the book" in response:
                return {
                    "response": "This topic is not covered in the book.",
                    "sources": []
                }

            # Filter sources based on confidence threshold
            sources = [
                {
                    "id": result["id"],
                    "content": result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"],  # Truncate for brevity
                    "score": result["score"],
                    "metadata": result["metadata"]
                }
                for result in search_results if result["score"] > 0.5
            ]

            return {
                "response": response,
                "sources": sources,
                "confidence_score": confidence_score
            }
        except Exception as e:
            return {
                "response": f"An error occurred while generating the response: {str(e)}",
                "sources": [],
                "confidence_score": 0.0
            }

# Global instance
rag_chain = RAGChain()