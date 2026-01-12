"""
===============================================================================
RAG.PY - Retrieval-Augmented Generation Pipeline
===============================================================================
A.B.E.L. Project - Personalized AI responses using memory
This is the core of A.B.E.L.'s learning capability!
===============================================================================
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.services.gemini.client import get_gemini_client
from app.services.memory.vector_store import SearchResult, get_vector_store

logger = logging.getLogger(__name__)


@dataclass
class RAGContext:
    """Context retrieved for RAG."""

    memories: List[SearchResult]
    profile_summary: str
    recent_topics: List[str]


@dataclass
class RAGResponse:
    """Response with context used."""

    response: str
    context_used: List[str]
    new_learnings: List[Dict[str, Any]]


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline for A.B.E.L.

    This makes A.B.E.L. truly personal:
    1. Retrieves relevant memories about the user
    2. Builds personalized context
    3. Generates contextually aware responses
    4. Extracts new learnings from conversations
    """

    def __init__(self):
        """Initialize RAG pipeline."""
        self.vector_store = get_vector_store()
        self.gemini = get_gemini_client()

    async def retrieve_context(
        self,
        user_id: str,
        query: str,
        max_memories: int = 5,
    ) -> RAGContext:
        """
        Retrieve relevant context for a user query.

        Args:
            user_id: User ID
            query: User's message/query
            max_memories: Maximum memories to retrieve

        Returns:
            RAGContext with relevant memories
        """
        try:
            # Search for relevant memories
            memories = await self.vector_store.search_memories(
                user_id=user_id,
                query=query,
                limit=max_memories,
                min_similarity=0.5,
            )

            # Build profile summary from high-importance memories
            profile_memories = await self.vector_store.get_user_memories(
                user_id=user_id,
                limit=10,
            )

            profile_parts = []
            for mem in profile_memories[:5]:
                if mem.importance >= 0.7:
                    profile_parts.append(f"- {mem.content}")

            profile_summary = "\n".join(profile_parts) if profile_parts else ""

            # Extract recent topics (from metadata if available)
            recent_topics = []
            for result in memories:
                if result.entry.metadata.get("topics"):
                    recent_topics.extend(result.entry.metadata["topics"])

            return RAGContext(
                memories=memories,
                profile_summary=profile_summary,
                recent_topics=list(set(recent_topics))[:5],
            )

        except Exception as e:
            logger.error(f"Context retrieval error: {e}")
            return RAGContext(memories=[], profile_summary="", recent_topics=[])

    async def generate_with_context(
        self,
        user_id: str,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> RAGResponse:
        """
        Generate a response using retrieved context.

        This is where A.B.E.L. becomes personal!

        Args:
            user_id: User ID
            message: User's message
            history: Conversation history

        Returns:
            RAGResponse with personalized response
        """
        try:
            # Retrieve relevant context
            context = await self.retrieve_context(user_id, message)

            # Build context string for the prompt
            context_parts = []

            if context.profile_summary:
                context_parts.append(f"Ce que je sais sur l'utilisateur:\n{context.profile_summary}")

            if context.memories:
                memory_texts = []
                for result in context.memories:
                    memory_texts.append(
                        f"[{result.entry.category}] {result.entry.content}"
                    )
                context_parts.append(f"Souvenirs pertinents:\n" + "\n".join(memory_texts))

            if context.recent_topics:
                context_parts.append(f"Sujets récents: {', '.join(context.recent_topics)}")

            # Build system instruction with context
            system_instruction = self._build_system_prompt(
                context_str="\n\n".join(context_parts) if context_parts else None
            )

            # Generate response with Gemini
            response_text = await self.gemini.generate_response(
                prompt=message,
                history=history,
                system_instruction=system_instruction,
            )

            # Extract new learnings from the conversation
            new_learnings = await self._extract_learnings(
                user_message=message,
                assistant_response=response_text,
            )

            # Store new learnings
            for learning in new_learnings:
                await self.vector_store.store_memory(
                    user_id=user_id,
                    category=learning["category"],
                    content=learning["content"],
                    importance=learning.get("importance", 0.5),
                    metadata={"source": "conversation", "auto_extracted": True},
                )

            # Update access counts for used memories
            for result in context.memories:
                await self.vector_store.increment_access(result.entry.id)

            return RAGResponse(
                response=response_text,
                context_used=[r.entry.content for r in context.memories],
                new_learnings=new_learnings,
            )

        except Exception as e:
            logger.error(f"RAG generation error: {e}")
            # Fallback to standard generation
            response_text = await self.gemini.generate_response(
                prompt=message,
                history=history,
            )
            return RAGResponse(
                response=response_text,
                context_used=[],
                new_learnings=[],
            )

    async def _extract_learnings(
        self,
        user_message: str,
        assistant_response: str,
    ) -> List[Dict[str, Any]]:
        """
        Extract new learnings about the user from conversation.

        Uses AI to identify:
        - Preferences expressed
        - Personal information shared
        - Habits mentioned
        - Interests revealed

        Returns:
            List of learnings to store
        """
        try:
            extraction_prompt = f"""Analyse cette conversation et extrais les informations importantes à mémoriser sur l'utilisateur.

Message utilisateur: "{user_message}"
Réponse assistant: "{assistant_response}"

Retourne un JSON avec les nouvelles informations à mémoriser (ou un tableau vide si rien d'important):
[
  {{"category": "preference|habit|knowledge|context", "content": "description concise", "importance": 0.0-1.0}}
]

Exemples de ce qui est important:
- Préférences: "Préfère les réponses courtes", "Aime le café"
- Habitudes: "Se lève tôt", "Travaille sur des projets IA"
- Connaissances: "Est développeur Python", "Étudie le machine learning"
- Contexte: "A un projet appelé X", "Travaille dans le domaine Y"

Retourne UNIQUEMENT le JSON, sans texte additionnel. Si rien n'est important, retourne []."""

            # Use a simple generation for extraction
            result = await self.gemini.generate_response(
                prompt=extraction_prompt,
                system_instruction="Tu es un assistant d'extraction de données. Retourne uniquement du JSON valide.",
            )

            # Parse JSON result
            import json
            try:
                # Clean the response (remove markdown code blocks if present)
                cleaned = result.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("\n", 1)[1]
                if cleaned.endswith("```"):
                    cleaned = cleaned.rsplit("```", 1)[0]
                cleaned = cleaned.strip()

                learnings = json.loads(cleaned)
                if isinstance(learnings, list):
                    return learnings
            except json.JSONDecodeError:
                logger.debug("No valid learnings extracted")

            return []

        except Exception as e:
            logger.warning(f"Learning extraction error: {e}")
            return []

    def _build_system_prompt(self, context_str: Optional[str] = None) -> str:
        """Build personalized system prompt."""
        base_prompt = """Tu es A.B.E.L. (Assistant Biométrique Enhanced Liaison), un assistant IA personnel et bienveillant.

Ton objectif est d'être un véritable compagnon intelligent, comme Jarvis pour Tony Stark:
- Tu mémorises les préférences et habitudes de l'utilisateur
- Tu t'adaptes à son style de communication
- Tu anticipes ses besoins basé sur ce que tu sais de lui
- Tu es proactif et suggères des choses pertinentes
- Tu traites l'utilisateur comme un ami, pas comme un client

Personnalité:
- Amical mais professionnel
- Curieux et engagé
- Proactif sans être envahissant
- Honnête et transparent
- Adaptatif au contexte"""

        if context_str:
            return f"""{base_prompt}

--- CONTEXTE PERSONNEL ---
{context_str}
--- FIN DU CONTEXTE ---

Utilise ces informations pour personnaliser tes réponses, mais ne les mentionne pas explicitement sauf si pertinent."""

        return base_prompt


# Global instance
_rag_pipeline: Optional[RAGPipeline] = None


def get_rag_pipeline() -> RAGPipeline:
    """Get or create RAGPipeline singleton."""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline
