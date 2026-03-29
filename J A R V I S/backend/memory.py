import json
import os
from pathlib import Path
from datetime import datetime
import re
from collections import Counter
from typing import List, Dict, Union, Tuple, Set
import logging
from mem0 import AsyncMemoryClient
from config import ConfigManager

config = ConfigManager()

logger = logging.getLogger(__name__)

class ConversationMemory:
    """Handles persistent conversation memory for users using Mem0 cloud storage (Async) or Local JSON"""
    
    def __init__(self, user_id: str, mem0_api_key: str = None):
        self.user_id = user_id
        self.local_file = Path(__file__).resolve().parent / "jarvis_memory.json"
        
        # Initialize Mem0 client - try multiple sources for API key
        api_key = mem0_api_key or config.get_api_key("mem0") or os.getenv("MEM0_API_KEY")
        
        if api_key:
            self.memory_client = AsyncMemoryClient(api_key=api_key)
            self.mode = "cloud"
            logger.info(f"ConversationMemory initialized for user: {user_id} with Mem0 cloud storage (Async)")
        else:
            self.memory_client = None
            self.mode = "local"
            logger.info(f"ConversationMemory initialized in LOCAL mode for user: {user_id} (Storage: {self.local_file})")
            
            # Create local file if it doesn't exist
            if not self.local_file.exists():
                with self.local_file.open('w', encoding='utf-8') as f:
                    json.dump({}, f)

    async def _load_local_data(self) -> List[Dict]:
        """Helper to read raw local JSON data"""
        try:
            if self.local_file.exists():
                with self.local_file.open('r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get(self.user_id, [])
            return []
        except Exception as e:
            logger.error(f"Error reading local memory file: {e}")
            return []

    async def _save_local_data(self, memories: List[Dict]):
        """Helper to write raw local JSON data"""
        try:
            all_data = {}
            self.local_file.parent.mkdir(parents=True, exist_ok=True)
            if self.local_file.exists():
                with self.local_file.open('r', encoding='utf-8') as f:
                    try:
                        all_data = json.load(f)
                    except json.JSONDecodeError:
                        all_data = {}
            
            all_data[self.user_id] = memories
            
            with self.local_file.open('w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error writing to local memory file: {e}")

    async def load_memory(self) -> List[Dict]:
        """Load all past conversations for this user"""
        try:
            if self.mode == "cloud":
                # Get all memories for this user
                memories = await self.memory_client.get_all(user_id=self.user_id)
                conversations = []
                if memories:
                    # Handle the results from Mem0 API
                    results = memories.get('results', []) if isinstance(memories, dict) else (memories if isinstance(memories, list) else [])
                    
                    for memory in results:
                        # Extract metadata which contains our conversation info
                        metadata = memory.get('metadata', {})
                        conversations.append({
                            'memory_id': memory.get('id'),
                            'timestamp': metadata.get('timestamp') or memory.get('created_at'),
                            'memory_text': memory.get('memory', ''),
                            'metadata': metadata
                        })
                logger.info(f"Loaded {len(conversations)} conversations from Mem0 for user {self.user_id}")
                return conversations
                
            else:
                # Local Mode
                memories = await self._load_local_data()
                # Local format is storing dicts directly
                logger.info(f"Loaded {len(memories)} conversations from Local JSON for user {self.user_id}")
                return memories
            
        except Exception as e:
            logger.error(f"Error loading memory: {e}")
            logger.exception("Full traceback:")
            return []
    
    async def save_conversation(self, conversation: Union[Dict, List, object]) -> Tuple[bool, str]:
        """Save a conversation to storage - returns (success, last_content)"""
        logger.info(f"save_conversation called for user {self.user_id} (Mode: {self.mode})")
        
        last_content = ""
        
        try:
            # Convert conversation to dict/list if it's an object with model_dump method
            if hasattr(conversation, 'model_dump'):
                conversation_data = conversation.model_dump()
            else:
                conversation_data = conversation
            
            # Handle list/dict normalization (same as before)
            if isinstance(conversation_data, list):
                all_messages = []
                for turn in conversation_data:
                    messages_in_turn = turn.get('messages', [])
                    all_messages.extend(messages_in_turn)
                
                latest_timestamp = max([turn.get('timestamp', 0) for turn in conversation_data if 'timestamp' in turn], default=None)
                timestamp = datetime.fromtimestamp(latest_timestamp).isoformat() if latest_timestamp else datetime.now().isoformat()
            else:
                all_messages = conversation_data.get('messages', [])
                timestamp = conversation_data.get('timestamp')
                if not timestamp:
                    timestamp = datetime.now().isoformat()
                elif isinstance(timestamp, (int, float)):
                    timestamp = datetime.fromtimestamp(timestamp).isoformat()
            
            # Format messages
            formatted_messages = []
            for msg in all_messages:
                msg_type = msg.get('type', 'message')
                role = msg.get('role', 'user')
                content = msg.get('content', [])
                
                if msg_type != 'message': continue
                
                if isinstance(content, list):
                    content_str = ' '.join([str(c) for c in content if c])
                else:
                    content_str = str(content) if content else ''
                
                if content_str and content_str.strip():
                    formatted_messages.append({
                        "role": role,
                        "content": content_str.strip()
                    })
                    last_content = content_str.strip()
            
            if not formatted_messages:
                logger.warning("No valid messages with content to save")
                return False, ""
            
            # Save based on Mode
            if self.mode == "cloud":
                if not self.memory_client:
                    return True, last_content # Should not happen based on init logic but safety check
                    
                await self.memory_client.add(
                    messages=formatted_messages,
                    user_id=self.user_id,
                    metadata={
                        "timestamp": timestamp,
                        "message_count": len(formatted_messages)
                    }
                )
                logger.info(f"Successfully saved to Mem0 Cloud")
                
            else:
                # Local Mode
                existing_memories = await self._load_local_data()
                
                # Create a simple memory entry
                memory_entry = {
                    "id": f"loc_{int(datetime.now().timestamp())}",
                    "memory": f"User conversation on {timestamp}. Last topic: {last_content[:50]}...",
                    "messages": formatted_messages, # Store full transcript locally
                    "timestamp": timestamp,
                    "metadata": {"source": "local_json"}
                }
                
                existing_memories.append(memory_entry)
                await self._save_local_data(existing_memories)
                logger.info(f"Successfully saved to Local JSON")
                
            return True, last_content
            
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            logger.exception("Full traceback:")
            return False, ""
    
    # ... (Keep existing simple methods with mode check if needed, or mostly unused by agent.py) ...
    async def get_all_memories(self) -> List[Dict]:
        return await self.load_memory()
    
    async def search_memories(self, query: str, limit: int = 10) -> List[Dict]:
        # Simple local search
        if self.mode == "local":
            memories = await self.load_memory()
            # Very basic text match
            return [m for m in memories if query.lower() in str(m).lower()][:limit]
        
        if not self.memory_client: return []
        return await self.memory_client.search(query=query, user_id=self.user_id, limit=limit)

    async def clear_all_memories(self) -> bool:
        if self.mode == "local":
            await self._save_local_data([])
            return True
        if self.memory_client:
            await self.memory_client.delete_all(user_id=self.user_id)
            return True
        return False

    def _count_sessions(self, memories: List[Dict]) -> int:
        """
        Estimate unique sessions using available timestamps.
        Falls back safely when timestamps are absent.
        """
        if not memories:
            return 0

        seen: Set[str] = set()
        for memory in memories:
            timestamp = (
                memory.get("timestamp")
                or memory.get("created_at")
                or memory.get("metadata", {}).get("timestamp")
            )
            if not timestamp:
                continue

            ts = str(timestamp)
            # Normalize rough session key to minute granularity.
            # This prevents splitting one conversation into too many sessions.
            session_key = ts[:16] if len(ts) >= 16 else ts
            seen.add(session_key)

        # If no timestamp-based sessions, fallback to memory count heuristic.
        return len(seen) if seen else len(memories)

    def _extract_topics(self, memories: List[Dict], max_topics: int = 12) -> List[str]:
        """
        Extract lightweight topic hints from memory text/messages.
        This is intentionally simple and deterministic (no extra model call).
        """
        text_chunks: List[str] = []

        for memory in memories:
            primary_text = (
                memory.get("memory")
                or memory.get("memory_text")
                or memory.get("text")
                or ""
            )
            if primary_text:
                text_chunks.append(str(primary_text))

            for msg in memory.get("messages", []):
                content = msg.get("content", "")
                if content:
                    text_chunks.append(str(content))

        if not text_chunks:
            return []

        combined = " ".join(text_chunks).lower()
        tokens = re.findall(r"\b[a-zA-Z][a-zA-Z]{2,}\b", combined)

        stopwords = {
            "the", "and", "for", "with", "this", "that", "have", "from", "your", "you",
            "are", "was", "were", "has", "had", "will", "would", "could", "should", "can",
            "sir", "please", "about", "what", "when", "where", "which", "there", "their",
            "them", "they", "our", "out", "into", "over", "under", "just", "very", "much",
            "help", "user", "assistant", "today", "tomorrow", "yesterday", "hello", "hi",
            "main", "ka", "ki", "hai", "aur", "nahi", "kya", "kar", "mein", "se", "par",
        }

        filtered = [t for t in tokens if t not in stopwords and len(t) > 2]
        if not filtered:
            return []

        top_terms = [word for word, _ in Counter(filtered).most_common(max_topics)]
        return top_terms

    def _personalisation_level(self, total_memories: int) -> str:
        if total_memories < 5:
            return "low"
        if total_memories < 20:
            return "medium"
        return "high"

    async def get_personalisation_score(self) -> Dict[str, Union[int, float, str, List[str]]]:
        """
        Memory Depth Score (MDS):
        Quantifies how deeply the assistant is personalized for this user.
        """
        memories = await self.get_all_memories()
        total_memories = len(memories)
        sessions_completed = self._count_sessions(memories)
        topics_covered = self._extract_topics(memories)
        topics_count = len(topics_covered)

        # Simple bounded score for observability dashboards and experiments.
        # Components:
        # - memory density (50%)
        # - session continuity (30%)
        # - topical breadth (20%)
        memory_component = min(total_memories / 20.0, 1.0) * 50.0
        session_component = min(sessions_completed / 10.0, 1.0) * 30.0
        topic_component = min(topics_count / 10.0, 1.0) * 20.0
        mds_score = round(memory_component + session_component + topic_component, 2)

        return {
            "total_memories": total_memories,
            "sessions_completed": sessions_completed,
            "topics_covered": topics_covered,
            "topics_covered_count": topics_count,
            "mds_score": mds_score,
            "personalisation_level": self._personalisation_level(total_memories),
        }
