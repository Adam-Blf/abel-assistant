"""
A.B.E.L - WebSocket API for Real-time Communication
"""

import json
from typing import Dict, Set
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.core.logging import logger
from app.brain.chat_service import ChatService
from app.brain.memory_service import MemoryService
from app.core.database import async_session_maker

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[str]] = {}  # channel -> connection_ids

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket connected: {client_id}")

    def disconnect(self, client_id: str):
        """Remove a WebSocket connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            # Remove from all subscriptions
            for channel in self.subscriptions.values():
                channel.discard(client_id)
            logger.info(f"WebSocket disconnected: {client_id}")

    async def send_personal(self, message: dict, client_id: str):
        """Send a message to a specific client."""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

    async def broadcast(self, message: dict, channel: str = "general"):
        """Broadcast a message to all clients in a channel."""
        if channel in self.subscriptions:
            for client_id in self.subscriptions[channel]:
                if client_id in self.active_connections:
                    await self.active_connections[client_id].send_json(message)

    async def broadcast_all(self, message: dict):
        """Broadcast a message to all connected clients."""
        for websocket in self.active_connections.values():
            await websocket.send_json(message)

    def subscribe(self, client_id: str, channel: str):
        """Subscribe a client to a channel."""
        if channel not in self.subscriptions:
            self.subscriptions[channel] = set()
        self.subscriptions[channel].add(client_id)

    def unsubscribe(self, client_id: str, channel: str):
        """Unsubscribe a client from a channel."""
        if channel in self.subscriptions:
            self.subscriptions[channel].discard(client_id)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/chat/{client_id}")
async def websocket_chat(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time chat.

    Message format:
    {
        "type": "message" | "subscribe" | "ping",
        "content": "...",
        "conversation_id": 123 (optional)
    }
    """
    await manager.connect(websocket, client_id)

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await manager.send_personal(
                    {"type": "error", "content": "Invalid JSON"}, client_id
                )
                continue

            msg_type = message.get("type", "message")

            # Handle ping
            if msg_type == "ping":
                await manager.send_personal(
                    {"type": "pong", "timestamp": datetime.utcnow().isoformat()},
                    client_id,
                )
                continue

            # Handle subscription
            if msg_type == "subscribe":
                channel = message.get("channel", "general")
                manager.subscribe(client_id, channel)
                await manager.send_personal(
                    {"type": "subscribed", "channel": channel}, client_id
                )
                continue

            # Handle chat message
            if msg_type == "message":
                content = message.get("content", "")
                conversation_id = message.get("conversation_id")

                if not content:
                    await manager.send_personal(
                        {"type": "error", "content": "Empty message"}, client_id
                    )
                    continue

                # Send typing indicator
                await manager.send_personal(
                    {"type": "typing", "status": True}, client_id
                )

                try:
                    # Process message
                    async with async_session_maker() as db:
                        chat_service = ChatService(db)
                        memory_service = MemoryService()

                        # Get memory context
                        memories = await memory_service.recall_memory(content, limit=3)
                        memory_context = None
                        if memories:
                            memory_context = "\n".join([m["content"] for m in memories])

                        # Generate response
                        result = await chat_service.process_message(
                            message=content,
                            conversation_id=conversation_id,
                            memory_context=memory_context,
                        )

                        # Store in memory
                        await memory_service.store_memory(
                            text=f"User: {content}\nAbel: {result['response']}",
                            memory_type="conversation",
                        )

                    # Send response
                    await manager.send_personal(
                        {
                            "type": "response",
                            "content": result["response"],
                            "conversation_id": result["conversation_id"],
                            "tokens_used": result["tokens_used"],
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                        client_id,
                    )

                except Exception as e:
                    logger.error(f"Chat processing error: {e}")
                    await manager.send_personal(
                        {"type": "error", "content": str(e)}, client_id
                    )

                finally:
                    # Stop typing indicator
                    await manager.send_personal(
                        {"type": "typing", "status": False}, client_id
                    )

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(client_id)


@router.websocket("/events/{client_id}")
async def websocket_events(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for system events and notifications.

    Clients can subscribe to channels:
    - "notifications": System notifications
    - "social": Social media updates
    - "emails": New email alerts
    - "calendar": Calendar reminders
    """
    await manager.connect(websocket, client_id)

    # Auto-subscribe to notifications
    manager.subscribe(client_id, "notifications")

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "subscribe":
                channel = message.get("channel")
                if channel:
                    manager.subscribe(client_id, channel)
                    await manager.send_personal(
                        {"type": "subscribed", "channel": channel}, client_id
                    )

            elif message.get("type") == "unsubscribe":
                channel = message.get("channel")
                if channel:
                    manager.unsubscribe(client_id, channel)
                    await manager.send_personal(
                        {"type": "unsubscribed", "channel": channel}, client_id
                    )

            elif message.get("type") == "ping":
                await manager.send_personal(
                    {"type": "pong", "timestamp": datetime.utcnow().isoformat()},
                    client_id,
                )

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"Events WebSocket error: {e}")
        manager.disconnect(client_id)


# Utility function to broadcast events (used by other modules)
async def broadcast_event(event_type: str, data: dict, channel: str = "notifications"):
    """Broadcast an event to all subscribed clients."""
    await manager.broadcast(
        {
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        },
        channel=channel,
    )
