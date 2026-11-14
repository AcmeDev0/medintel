"""
MedIntel AI — RAG (Retrieval-Augmented Generation) Engine.
Core intelligence service that powers regulatory Q&A with source citations.
"""

import os
from typing import Optional
from pathlib import Path

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from app.config import settings

# --- System Prompt ---
SYSTEM_PROMPT = """You are MedIntel AI, a regulatory intelligence assistant specializing in Nigerian (NAFDAC) and international healthcare regulations for medical devices, pharmaceuticals, and in-vitro diagnostics.

Your role is to provide accurate, actionable regulatory guidance to manufacturers, clinical engineers, regulatory affairs professionals, and drug producers.

CRITICAL RULES:
1. ALWAYS cite your sources. Reference specific regulation names, section numbers, and document titles.
2. If you are not certain about a specific requirement, say so explicitly. Never fabricate regulatory requirements.
3. Prioritize Nigerian (NAFDAC) regulations when the user doesn't specify a jurisdiction.
4. For questions outside your knowledge base, recommend the user consult with a qualified regulatory affairs professional.
5. Structure your responses clearly with headings, numbered steps, and bullet points when appropriate.
6. When providing step-by-step processes, include estimated timelines and fees where known.

JURISDICTION PRIORITY:
- Primary: NAFDAC (Nigeria), SON (Standards Organisation of Nigeria)
- Secondary: WHO guidelines, FDA (US), EU MDR/IVDR
- Tertiary: ISO standards (13485, 14971, etc.)

DISCLAIMER: Always end substantive regulatory advice with:
"⚠️ This guidance is for informational purposes only and does not constitute legal or regulatory advice. Always verify requirements directly with the relevant regulatory authority."

CONTEXT FROM KNOWLEDGE BASE:
{context}

USER QUESTION: {question}

Provide a thorough, well-structured response with specific citations to the source documents provided in the context."""

# --- Classification Prompt ---
CLASSIFICATION_PROMPT = """You are MedIntel AI's medical device classification engine. Based on the user's product description, classify the device according to NAFDAC's risk-based classification system.

NAFDAC Device Classification (aligned with GHTF/IMDRF):
- **Class A (Low Risk)**: Non-invasive devices, no contact with injured skin. Examples: bandages, hospital beds, wheelchairs, stethoscopes.
- **Class B (Low-Moderate Risk)**: Short-term invasive devices, devices for channeling/storing blood. Examples: hypodermic needles, surgical sutures, hearing aids, ultrasound probes.
- **Class C (Moderate-High Risk)**: Long-term invasive devices, devices releasing substances. Examples: ventilators, orthopedic implants (non-spinal), dialysis equipment.
- **Class D (High Risk)**: Life-sustaining/life-supporting devices, devices in direct contact with CNS/cardiovascular system. Examples: heart valves, pacemakers, spinal implants, defibrillators.

For Software as a Medical Device (SaMD):
- Consider the intended purpose and the seriousness of the condition it addresses.
- AI/ML-based devices may require additional regulatory documentation.

Provide:
1. **Recommended Classification** (Class A/B/C/D)
2. **Justification** — why this class, referencing NAFDAC classification rules
3. **Regulatory Pathway** — what registration process applies
4. **Key Requirements** — documents and testing needed for this class
5. **Estimated Timeline** — typical registration duration
6. **Similar Devices** — examples of approved devices in this class

PRODUCT DESCRIPTION: {description}

CONTEXT FROM KNOWLEDGE BASE:
{context}"""


class RAGEngine:
    """
    Retrieval-Augmented Generation engine for MedIntel AI.
    Manages the vector store, embeddings, and LLM chain.
    """

    _instance: Optional["RAGEngine"] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._vectorstore = None
        self._embeddings = None
        self._llm = None
        self._chain = None

    def _get_embeddings(self):
        """Initialize the embedding model."""
        if self._embeddings is None:
            self._embeddings = GoogleGenerativeAIEmbeddings(
                model=f"models/{settings.GEMINI_EMBEDDING_MODEL}",
                google_api_key=settings.GEMINI_API_KEY,
            )
        return self._embeddings

    def _get_llm(self):
        """Initialize the LLM."""
        if self._llm is None:
            self._llm = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=settings.GEMINI_API_KEY,
                temperature=settings.TEMPERATURE,
                max_output_tokens=4096,
            )
        return self._llm

    def _get_vectorstore(self):
        """Initialize or connect to the ChromaDB vector store."""
        if self._vectorstore is None:
            persist_dir = Path(settings.CHROMA_PERSIST_DIR)
            persist_dir.mkdir(parents=True, exist_ok=True)

            self._vectorstore = Chroma(
                collection_name=settings.CHROMA_COLLECTION_NAME,
                embedding_function=self._get_embeddings(),
                persist_directory=str(persist_dir),
            )
        return self._vectorstore

    def get_retriever(self, k: int = None):
        """Get the vector store retriever."""
        k = k or settings.TOP_K_RESULTS
        return self._get_vectorstore().as_retriever(
            search_type="similarity",
            search_kwargs={"k": k},
        )

    async def query(self, question: str) -> dict:
        """
        Process a regulatory question through the RAG pipeline.
        Returns the answer with source citations.
        """
        retriever = self.get_retriever()
        llm = self._get_llm()

        # Retrieve relevant documents
        docs = retriever.invoke(question)

        # Format context from retrieved documents
        context_parts = []
        sources = []
        for i, doc in enumerate(docs):
            source_name = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "N/A")
            section = doc.metadata.get("section", "")

            context_parts.append(
                f"[Source {i+1}: {source_name}, Page {page}]\n{doc.page_content}"
            )
            sources.append({
                "document": source_name,
                "page": page,
                "section": section,
                "excerpt": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
            })

        context = "\n\n---\n\n".join(context_parts) if context_parts else "No relevant documents found in the knowledge base."

        # Create and invoke the chain
        prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)
        chain = prompt | llm | StrOutputParser()

        response = chain.invoke({
            "context": context,
            "question": question,
        })

        return {
            "answer": response,
            "sources": sources,
            "query": question,
        }

    async def classify_device(self, description: str) -> dict:
        """
        Classify a medical device based on its description.
        """
        retriever = self.get_retriever()
        llm = self._get_llm()

        # Retrieve classification-related documents
        docs = retriever.invoke(f"medical device classification {description}")

        context_parts = []
        sources = []
        for i, doc in enumerate(docs):
            source_name = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "N/A")

            context_parts.append(
                f"[Source {i+1}: {source_name}, Page {page}]\n{doc.page_content}"
            )
            sources.append({
                "document": source_name,
                "page": page,
                "excerpt": doc.page_content[:200] + "...",
            })

        context = "\n\n---\n\n".join(context_parts) if context_parts else "No specific classification documents found."

        prompt = ChatPromptTemplate.from_template(CLASSIFICATION_PROMPT)
        chain = prompt | llm | StrOutputParser()

        response = chain.invoke({
            "context": context,
            "description": description,
        })

        return {
            "classification": response,
            "sources": sources,
            "device_description": description,
        }

    def get_collection_stats(self) -> dict:
        """Get statistics about the knowledge base."""
        try:
            vs = self._get_vectorstore()
            collection = vs._collection
            count = collection.count()
            return {
                "total_chunks": count,
                "collection_name": settings.CHROMA_COLLECTION_NAME,
                "status": "ready" if count > 0 else "empty",
            }
        except Exception as e:
            return {
                "total_chunks": 0,
                "collection_name": settings.CHROMA_COLLECTION_NAME,
                "status": f"error: {str(e)}",
            }


# Singleton instance
rag_engine = RAGEngine()
