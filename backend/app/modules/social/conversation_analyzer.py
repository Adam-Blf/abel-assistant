"""
A.B.E.L - Conversation Analyzer (Tone & Context Analysis)
"""

from typing import Optional, List, Dict, Any
from enum import Enum

from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logging import logger


class ToneType(str, Enum):
    FRIENDLY = "friendly"
    FORMAL = "formal"
    URGENT = "urgent"
    PASSIVE_AGGRESSIVE = "passive_aggressive"
    SARCASTIC = "sarcastic"
    NEUTRAL = "neutral"
    ANGRY = "angry"
    EXCITED = "excited"
    FLIRTY = "flirty"
    CONFUSED = "confused"


class ConversationAnalyzer:
    """
    Analyze conversations for tone, context, and generate appropriate responses.

    Uses GPT-4 for:
    - Tone analysis
    - Context understanding
    - Response suggestions
    - Directive-based response generation
    """

    ANALYSIS_PROMPT = """Tu es un expert en analyse de conversations. Analyse la conversation suivante et fournis:

1. TONE: Le ton général du dernier message (choisir parmi: friendly, formal, urgent, passive_aggressive, sarcastic, neutral, angry, excited, flirty, confused)
2. CONTEXT: Un résumé du contexte de la conversation (2-3 phrases)
3. INTENT: L'intention probable de l'interlocuteur
4. SUGGESTED_RESPONSES: 3 suggestions de réponses possibles (courtes)

Réponds en JSON valide avec cette structure:
{
    "tone": "...",
    "context_summary": "...",
    "sender_intent": "...",
    "suggested_responses": ["...", "...", "..."],
    "urgency_level": "low|medium|high",
    "requires_action": true/false
}

CONVERSATION:
{conversation}

DERNIER MESSAGE DE {sender}:
{last_message}
"""

    RESPONSE_PROMPT = """Tu es A.B.E.L, un assistant IA qui aide à rédiger des réponses pour les réseaux sociaux.

ANALYSE DE LA CONVERSATION:
Ton détecté: {tone}
Contexte: {context}
Intention de l'expéditeur: {intent}

DIRECTIVE DE L'UTILISATEUR:
{directive}

Génère une réponse appropriée en suivant la directive. La réponse doit:
- Être naturelle et adaptée au ton de la conversation
- Suivre exactement les instructions de la directive
- Ne pas dépasser 500 caractères
- Être en français sauf si la conversation est dans une autre langue

Réponds uniquement avec le texte de la réponse, sans guillemets ni explication.
"""

    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def analyze_conversation(
        self,
        conversation_text: str,
        last_message: str,
        sender_username: str,
    ) -> Dict[str, Any]:
        """
        Analyze a conversation for tone and context.

        Args:
            conversation_text: Full conversation history
            last_message: The most recent message to respond to
            sender_username: Username of the sender

        Returns:
            Analysis results with tone, context, and suggestions
        """
        try:
            prompt = self.ANALYSIS_PROMPT.format(
                conversation=conversation_text,
                last_message=last_message,
                sender=sender_username,
            )

            response = await self.openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un expert en analyse de conversations. Réponds toujours en JSON valide.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500,
                temperature=0.3,
            )

            # Parse JSON response
            import json
            result_text = response.choices[0].message.content.strip()

            # Clean up potential markdown
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]

            analysis = json.loads(result_text)

            logger.info(f"Analyzed conversation - Tone: {analysis.get('tone')}")

            return {
                "tone": analysis.get("tone", "neutral"),
                "context_summary": analysis.get("context_summary", ""),
                "sender_intent": analysis.get("sender_intent", ""),
                "suggested_responses": analysis.get("suggested_responses", []),
                "urgency_level": analysis.get("urgency_level", "low"),
                "requires_action": analysis.get("requires_action", False),
            }

        except Exception as e:
            logger.error(f"Error analyzing conversation: {e}")
            return {
                "tone": "neutral",
                "context_summary": "Unable to analyze conversation",
                "sender_intent": "unknown",
                "suggested_responses": [],
                "urgency_level": "low",
                "requires_action": False,
                "error": str(e),
            }

    async def generate_response(
        self,
        analysis: Dict[str, Any],
        directive: str,
    ) -> str:
        """
        Generate a response based on analysis and user directive.

        Args:
            analysis: Conversation analysis from analyze_conversation()
            directive: User's instruction for the response

        Returns:
            Generated response text
        """
        try:
            prompt = self.RESPONSE_PROMPT.format(
                tone=analysis.get("tone", "neutral"),
                context=analysis.get("context_summary", ""),
                intent=analysis.get("sender_intent", ""),
                directive=directive,
            )

            response = await self.openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es A.B.E.L, un assistant IA sarcastique mais serviable.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=200,
                temperature=0.7,
            )

            generated = response.choices[0].message.content.strip()

            logger.info(f"Generated response: {generated[:50]}...")

            return generated

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return ""

    async def quick_reply_suggestions(
        self,
        last_message: str,
        context: Optional[str] = None,
    ) -> List[str]:
        """
        Generate quick reply suggestions for a message.

        Args:
            last_message: The message to reply to
            context: Optional additional context

        Returns:
            List of 3-5 quick reply suggestions
        """
        try:
            prompt = f"""Génère 4 réponses rapides possibles pour ce message:

MESSAGE: {last_message}
{f"CONTEXTE: {context}" if context else ""}

Les réponses doivent être:
- Courtes (moins de 50 caractères chacune)
- Variées en ton (neutre, amical, professionnel, décontracté)
- Naturelles

Réponds avec une liste JSON de strings uniquement."""

            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.8,
            )

            import json
            result = response.choices[0].message.content.strip()

            # Parse JSON
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]

            suggestions = json.loads(result)

            return suggestions if isinstance(suggestions, list) else []

        except Exception as e:
            logger.error(f"Error generating quick replies: {e}")
            return ["👍", "Merci!", "Je te réponds plus tard", "OK!"]

    async def detect_urgency(self, message: str) -> str:
        """
        Detect urgency level of a message.

        Returns: "low", "medium", or "high"
        """
        urgent_keywords = [
            "urgent", "asap", "immédiatement", "maintenant", "vite",
            "emergency", "aide", "help", "problème", "erreur", "bug",
            "!!!", "???", "stp", "svp", "please"
        ]

        message_lower = message.lower()

        # Check for urgent keywords
        urgent_count = sum(1 for kw in urgent_keywords if kw in message_lower)

        if urgent_count >= 2 or "!!!" in message:
            return "high"
        elif urgent_count >= 1:
            return "medium"
        return "low"
