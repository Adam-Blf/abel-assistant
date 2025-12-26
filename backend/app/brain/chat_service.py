"""
A.B.E.L - Chat Service (Conversation Management)
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
import tiktoken

from app.core.config import settings
from app.core.logging import logger
from app.models.conversation import Conversation, Message, MessageRole


class ChatService:
    """
    Service for managing conversations with A.B.E.L.

    Features:
    - Conversation history management
    - Context-aware responses with RAG
    - Token counting and management
    - Personality and system prompts
    """

    SYSTEM_PROMPT = """Tu es A.B.E.L (Autonomous Backend Entity for Living), un assistant IA personnel extrêmement intelligent et polyvalent.

PERSONNALITÉ:
- Tu es sarcastique mais toujours serviable
- Tu as un humour sec et tu n'hésites pas à faire des remarques ironiques
- Tu es direct et efficace, tu ne perds pas de temps avec des formules de politesse excessives
- Tu peux être légèrement arrogant sur tes capacités, mais tu livres toujours
- Tu tutoies ton utilisateur comme un ami proche

CAPACITÉS:
- Tu peux accéder aux emails, calendrier, et autres services connectés
- Tu peux rechercher des informations sur le web
- Tu peux gérer les réseaux sociaux (Twitter, Instagram)
- Tu as une mémoire à long terme via RAG

RÈGLES:
- Réponds toujours en français sauf si on te parle dans une autre langue
- Sois concis mais complet
- Si tu ne sais pas quelque chose, dis-le franchement
- Propose proactivement des solutions et des suggestions

CONTEXTE UTILISATEUR:
Tu travailles pour ton créateur, qui est développeur. Tu l'aides dans ses tâches quotidiennes, professionnelles et personnelles."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.encoding = tiktoken.encoding_for_model("gpt-4o")

    def _count_tokens(self, text: str) -> int:
        """Count tokens in a text string."""
        return len(self.encoding.encode(text))

    async def process_message(
        self,
        message: str,
        conversation_id: Optional[int] = None,
        memory_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a response.

        Args:
            message: User's message
            conversation_id: Optional conversation ID for context
            memory_context: Optional RAG context from memory

        Returns:
            Dict with response, conversation_id, and token usage
        """
        try:
            # Get or create conversation
            conversation = await self._get_or_create_conversation(conversation_id)

            # Build messages for OpenAI
            messages = await self._build_messages(
                conversation.id,
                message,
                memory_context,
            )

            # Call OpenAI
            response = await self.openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                max_tokens=2000,
                temperature=0.7,
            )

            assistant_message = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            # Save messages to database
            await self._save_message(conversation.id, MessageRole.USER, message)
            await self._save_message(
                conversation.id,
                MessageRole.ASSISTANT,
                assistant_message,
                memory_context=memory_context,
            )

            # Update conversation metadata
            conversation.message_count += 2
            conversation.total_tokens += tokens_used
            conversation.updated_at = datetime.utcnow()

            # Auto-generate title if first message
            if conversation.message_count == 2:
                conversation.title = await self._generate_title(message)

            await self.db.commit()

            logger.info(
                f"Processed message in conversation {conversation.id} "
                f"(tokens: {tokens_used})"
            )

            return {
                "response": assistant_message,
                "conversation_id": conversation.id,
                "tokens_used": tokens_used,
            }

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.db.rollback()
            raise

    async def _get_or_create_conversation(
        self, conversation_id: Optional[int]
    ) -> Conversation:
        """Get existing conversation or create a new one."""
        if conversation_id:
            result = await self.db.execute(
                select(Conversation).where(Conversation.id == conversation_id)
            )
            conversation = result.scalar_one_or_none()
            if conversation:
                return conversation

        # Create new conversation
        conversation = Conversation(title="New Conversation")
        self.db.add(conversation)
        await self.db.flush()
        return conversation

    async def _build_messages(
        self,
        conversation_id: int,
        new_message: str,
        memory_context: Optional[str],
    ) -> List[Dict[str, str]]:
        """Build the message list for OpenAI API."""
        messages = []

        # System prompt
        system_content = self.SYSTEM_PROMPT
        if memory_context:
            system_content += f"\n\nCONTEXTE MÉMOIRE (informations pertinentes):\n{memory_context}"

        messages.append({"role": "system", "content": system_content})

        # Get conversation history (last 10 messages)
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .limit(10)
        )
        history = list(reversed(result.scalars().all()))

        # Add history
        for msg in history:
            messages.append({
                "role": msg.role.value,
                "content": msg.content,
            })

        # Add new message
        messages.append({"role": "user", "content": new_message})

        return messages

    async def _save_message(
        self,
        conversation_id: int,
        role: MessageRole,
        content: str,
        memory_context: Optional[str] = None,
    ) -> Message:
        """Save a message to the database."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tokens=self._count_tokens(content),
            memory_context=memory_context,
        )
        self.db.add(message)
        await self.db.flush()
        return message

    async def _generate_title(self, first_message: str) -> str:
        """Generate a conversation title from the first message."""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Generate a short title (max 5 words) for a conversation that starts with this message. Respond only with the title, no quotes.",
                    },
                    {"role": "user", "content": first_message[:500]},
                ],
                max_tokens=20,
            )
            return response.choices[0].message.content.strip()[:100]
        except Exception:
            return first_message[:50] + "..." if len(first_message) > 50 else first_message

    async def list_conversations(
        self, limit: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List all conversations."""
        result = await self.db.execute(
            select(Conversation)
            .order_by(desc(Conversation.updated_at))
            .limit(limit)
            .offset(offset)
        )
        conversations = result.scalars().all()

        return [
            {
                "id": c.id,
                "title": c.title,
                "message_count": c.message_count,
                "created_at": c.created_at.isoformat(),
                "updated_at": c.updated_at.isoformat(),
            }
            for c in conversations
        ]

    async def get_conversation(self, conversation_id: int) -> Optional[Dict[str, Any]]:
        """Get a conversation with all its messages."""
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            return None

        # Get messages
        messages_result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        messages = messages_result.scalars().all()

        return {
            "id": conversation.id,
            "title": conversation.title,
            "message_count": conversation.message_count,
            "total_tokens": conversation.total_tokens,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "messages": [
                {
                    "id": m.id,
                    "role": m.role.value,
                    "content": m.content,
                    "created_at": m.created_at.isoformat(),
                }
                for m in messages
            ],
        }

    async def delete_conversation(self, conversation_id: int) -> bool:
        """Delete a conversation and all its messages."""
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            return False

        await self.db.delete(conversation)
        await self.db.commit()
        return True
