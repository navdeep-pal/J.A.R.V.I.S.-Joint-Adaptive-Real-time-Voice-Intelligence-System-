"""
backend/memory_worker.py

Background async task that continuously monitors the conversation history
and persists new messages to the memory storage backend (Mem0 or local JSON).
"""
import asyncio
import time
import logging
from memory import ConversationMemory
from pydantic import BaseModel
from config import ConfigManager

config = ConfigManager()

logger = logging.getLogger(__name__)


class MemoryExtractor:
    """
    Background task that checks for new chat messages every few seconds
    and saves them to persistent storage without blocking the voice session.
    """

    def __init__(self):
        self.saved_message_count = 0

    def _serialize_for_hash(self, obj):
        """
        Recursively converts Pydantic objects or nested data into serializable dicts.
        """
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        elif isinstance(obj, dict):
            return {k: self._serialize_for_hash(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_for_hash(item) for item in obj]
        return obj

    async def run(self, session):
        """
        Main polling loop. Checks for new messages every 3 seconds and saves them.
        """
        user_id = config.get_user_id()
        mem0_key = config.get_mem0_key()

        memory = ConversationMemory(user_id=user_id, mem0_api_key=mem0_key)
        logger.info(f"MemoryExtractor started for user: {user_id}")

        while True:
            await asyncio.sleep(3)

            current_chat_history = session

            if len(current_chat_history) > self.saved_message_count:
                new_count = len(current_chat_history) - self.saved_message_count
                logger.info(f"{new_count} new message(s) detected. Persisting...")

                new_messages = current_chat_history[self.saved_message_count:]

                for message in new_messages:
                    serialized = self._serialize_for_hash(message)
                    conversation_wrapper = {
                        "messages": [serialized],
                        "timestamp": time.time(),
                    }

                    success, _ = await memory.save_conversation(conversation_wrapper)

                    if success:
                        logger.debug(f"Saved message: {getattr(message, 'id', 'unknown')}")
                    else:
                        logger.warning(f"Failed to save message: {getattr(message, 'id', 'unknown')}")

                self.saved_message_count = len(current_chat_history)
