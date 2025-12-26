"""
A.B.E.L - Chat API Endpoints
"""

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import logger
from app.brain.chat_service import ChatService
from app.brain.memory_service import MemoryService

router = APIRouter()


class ChatMessage(BaseModel):
    """Chat message input schema."""

    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[int] = None
    use_memory: bool = Field(default=True, description="Use RAG memory context")
    stream: bool = Field(default=False, description="Stream response")


class ChatResponse(BaseModel):
    """Chat response schema."""

    response: str
    conversation_id: int
    memory_context: Optional[str] = None
    tokens_used: int
    timestamp: str


class ConversationSummary(BaseModel):
    """Conversation summary schema."""

    id: int
    title: str
    message_count: int
    last_message: Optional[str] = None
    created_at: str
    updated_at: str


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatMessage,
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message to A.B.E.L and receive a response.

    - Uses RAG to retrieve relevant memories for context
    - Maintains conversation history
    - Supports streaming responses
    """
    try:
        chat_service = ChatService(db)
        memory_service = MemoryService()

        # Retrieve memory context if enabled
        memory_context = None
        if request.use_memory:
            memories = await memory_service.recall_memory(request.message, limit=5)
            if memories:
                memory_context = "\n".join([m["content"] for m in memories])

        # Generate response
        result = await chat_service.process_message(
            message=request.message,
            conversation_id=request.conversation_id,
            memory_context=memory_context,
        )

        # Store the interaction in memory
        await memory_service.store_memory(
            text=f"User: {request.message}\nAbel: {result['response']}",
            memory_type="conversation",
            metadata={"conversation_id": result["conversation_id"]},
        )

        return ChatResponse(
            response=result["response"],
            conversation_id=result["conversation_id"],
            memory_context=memory_context,
            tokens_used=result["tokens_used"],
            timestamp=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations", response_model=List[ConversationSummary])
async def list_conversations(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List all conversations."""
    try:
        chat_service = ChatService(db)
        conversations = await chat_service.list_conversations(limit=limit, offset=offset)
        return conversations
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific conversation with all messages."""
    try:
        chat_service = ChatService(db)
        conversation = await chat_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a conversation and all its messages."""
    try:
        chat_service = ChatService(db)
        success = await chat_service.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return {"status": "deleted", "conversation_id": conversation_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick")
async def quick_chat(message: str):
    """
    Quick chat endpoint without persistence.
    Useful for one-off questions.
    """
    try:
        from openai import AsyncOpenAI
        from app.core.config import settings

        client = AsyncOpenAI(api_key=settings.openai_api_key)

        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es A.B.E.L (Autonomous Backend Entity for Living), "
                        "un assistant IA personnel intelligent, sarcastique mais serviable. "
                        "Tu réponds en français sauf si on te parle dans une autre langue."
                    ),
                },
                {"role": "user", "content": message},
            ],
            max_tokens=1000,
        )

        return {
            "response": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens,
        }

    except Exception as e:
        logger.error(f"Quick chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
