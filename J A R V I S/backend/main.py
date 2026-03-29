"""
backend/main.py

Entry point for the J.A.R.V.I.S. real-time voice agent.
Uses LiveKit Agents SDK with Google Gemini Native Audio.
"""
import asyncio
import os
import sys
import logging
import time
from uuid import uuid4
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, ChatContext
from livekit.plugins import google, noise_cancellation, openai

from prompts import load_prompts
from memory_worker import MemoryExtractor
from config import ConfigManager
from evaluation_logger import log_experiment_event
from document_store import DocumentKnowledgeBase, create_document_tools

# ─── Encoding Fix (Windows / Non-UTF-8 terminals) ────────────────────────────
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ─── Config & Env ────────────────────────────────────────────────────────────
config = ConfigManager()
load_dotenv()


# ─── Agent Class ─────────────────────────────────────────────────────────────
class Assistant(Agent):
    """Wrapper around LiveKit Agent for J.A.R.V.I.S. sessions."""

    def __init__(self, chat_ctx, llm_instance, instructions_text, tools=None) -> None:
        super().__init__(
            instructions=instructions_text,
            chat_ctx=chat_ctx,
            llm=llm_instance,
            tools=tools or []
        )


# ─── Agent Entrypoint ────────────────────────────────────────────────────────
async def entrypoint(ctx: agents.JobContext):
    """Main entrypoint called by LiveKit for each new room connection."""

    # Reload config on each new session to pick up any changes
    config.load_config()
    session_id = str(uuid4())

    user_id = config.get_user_id()
    full_name = config.get_full_name()
    mem0_key = config.get_mem0_key()
    mds_enabled = config.is_mds_enabled()
    knowledge_base = DocumentKnowledgeBase(config.get_documents_dir())

    # ── Init Memory ───────────────────────────────────────────────────────────
    from memory import ConversationMemory
    memory_manager = ConversationMemory(user_id=user_id, mem0_api_key=mem0_key)

    async def _fetch_memories() -> str:
        try:
            all_memories = await memory_manager.get_all_memories()
            formatted = [
                m.get("memory") or m.get("text") or m.get("memory_text")
                for m in all_memories
            ]
            formatted = [t for t in formatted if t]
            if formatted:
                logger.info(f"Loaded {len(formatted)} past memory items.")
                return "\n\nKNOWN USER HISTORY:\n" + "\n".join(formatted)
            return "\n(No previous history found.)"
        except Exception as e:
            logger.error(f"Memory fetch error: {e}")
            return "\n(Memory system unavailable)"

    async def _fetch_personalisation() -> dict:
        try:
            return await memory_manager.get_personalisation_score()
        except Exception as e:
            logger.warning(f"Personalisation score unavailable: {e}")
            return {
                "mds_score": 0,
                "personalisation_level": "low",
                "topics_covered": [],
            }

    async def _fetch_document_status() -> dict:
        try:
            return await knowledge_base.get_status()
        except Exception as e:
            logger.warning(f"Document knowledge base unavailable: {e}")
            return {
                "documents_dir": config.get_documents_dir(),
                "document_count": 0,
                "document_names": [],
            }

    # ── Parallel Startup: Memory + MDS, then prompt compile ──────────────────
    memory_str, personalisation_profile, document_status = await asyncio.gather(
        _fetch_memories(),
        _fetch_personalisation(),
        _fetch_document_status(),
    )
    instructions_prompt, reply_prompt = await load_prompts(
        personalisation_profile,
        mds_enabled=mds_enabled,
        document_status=document_status,
    )
    logger.info(f"Session started — User: {full_name} | ID: {user_id}")
    logger.info(
        "MDS — Score: %s | Level: %s | Topics: %s",
        personalisation_profile.get("mds_score"),
        personalisation_profile.get("personalisation_level"),
        personalisation_profile.get("topics_covered_count", 0),
    )
    logger.info(
        "Docs — Count: %s | Folder: %s",
        document_status.get("document_count", 0),
        document_status.get("documents_dir"),
    )

    # ── LLM Provider Selection ────────────────────────────────────────────────
    llm_config = config.get_llm_config()
    provider = llm_config.get("provider", "google")
    model_name = llm_config.get("model", "gemini-2.5-flash-native-audio-preview-09-2025")
    default_voice = "Puck" if provider == "google" else "alloy"
    voice_name = llm_config.get("voice", default_voice)

    logger.info(f"LLM — Provider: {provider} | Model: {model_name} | Voice: {voice_name}")
    log_experiment_event(
        "session_start",
        {
            "session_id": session_id,
            "user_id": user_id,
            "mds_enabled": mds_enabled,
            "llm_provider": provider,
            "llm_model": model_name,
            "voice": voice_name,
            "mds_score": personalisation_profile.get("mds_score", 0),
            "personalisation_level": (
                personalisation_profile.get("personalisation_level", "low")
                if mds_enabled
                else "baseline"
            ),
            "topics_covered_count": personalisation_profile.get("topics_covered_count", 0),
            "memory_items_loaded": memory_str.count("\n") if "KNOWN USER HISTORY" in memory_str else 0,
            "document_count": document_status.get("document_count", 0),
        },
    )

    llm_instance = None
    if provider == "google":
        google_api_key = config.get_api_key("google")
        if not google_api_key:
            raise ValueError("Google API key is required. Please add it to user_config.json.")

        # Try models in priority order; fall back gracefully
        GEMINI_MODELS = list(dict.fromkeys([
            model_name,
            "gemini-2.5-flash-native-audio-preview-12-2025",
            "gemini-2.0-flash-exp",
            "gemini-2.5-flash-native-audio-preview-09-2025",
        ]))

        for candidate in GEMINI_MODELS:
            try:
                llm_instance = google.beta.realtime.RealtimeModel(
                    model=candidate,
                    api_key=google_api_key,
                    voice=voice_name,
                )
                logger.info(f"Gemini model selected: {candidate}")
                break
            except Exception as e:
                logger.warning(f"Model {candidate} unavailable: {e}")

        if llm_instance is None:
            raise ValueError("All Gemini models failed. Check your API key and quota.")

    elif provider == "openai":
        openai_api_key = config.get_api_key("openai")
        if not openai_api_key:
            raise ValueError("OpenAI API key is required. Please add it to user_config.json.")
        llm_instance = openai.realtime.RealtimeModel(
            model=model_name,
            api_key=openai_api_key,
            voice=voice_name,
        )

    else:
        logger.warning(f"Unknown provider '{provider}'. Falling back to Google.")
        google_api_key = config.get_api_key("google")
        if not google_api_key:
            raise ValueError("Google API key is required for fallback provider.")
        llm_instance = google.beta.realtime.RealtimeModel(
            model="gemini-2.5-flash-native-audio-preview-09-2025",
            api_key=google_api_key,
            voice="Puck",
        )

    # ── Session Setup ─────────────────────────────────────────────────────────
    session = AgentSession(preemptive_generation=True)
    current_ctx = session.history.items

    initial_ctx = ChatContext()
    initial_ctx.add_message(
        role="assistant",
        content=(
            f"The user's name is {full_name}. Internal ID: {user_id}."
            f"{memory_str}{await knowledge_base.build_prompt_context()}"
        ),
    )

    # ── MCP Tool Loading (n8n — Gmail, Drive) ─────────────────────────────────
    runtime_tools = list(create_document_tools(knowledge_base))
    mcp_tools = []
    n8n_url = config.get_n8n_url()
    if n8n_url:
        try:
            from mcp_client.server import MCPServerSse
            from mcp_client.agent_tools import MCPToolsIntegration
            logger.info(f"Connecting to n8n MCP server: {n8n_url}")
            n8n_server = MCPServerSse(
                {"url": n8n_url, "timeout": 10, "sse_read_timeout": 300},
                name="n8n-gmail-drive",
                cache_tools_list=True,
            )
            mcp_tools = await MCPToolsIntegration.prepare_dynamic_tools(
                [n8n_server], auto_connect=True
            )
            tool_names = [getattr(t, "__name__", "?") for t in mcp_tools]
            logger.info(f"Loaded {len(mcp_tools)} MCP tools: {tool_names}")
        except Exception as e:
            logger.warning(f"n8n MCP not available — Gmail/Drive tools skipped: {e}")
    else:
        logger.info("n8n_url not configured — MCP tools disabled.")
    all_tools = [*runtime_tools, *mcp_tools]

    # ── Launch Session ────────────────────────────────────────────────────────
    await session.start(
        room=ctx.room,
        agent=Assistant(
            chat_ctx=initial_ctx,
            llm_instance=llm_instance,
            instructions_text=instructions_prompt,
            tools=all_tools,
        ),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        ),
    )
    log_experiment_event(
        "session_connected",
        {
            "session_id": session_id,
            "user_id": user_id,
            "room_name": getattr(ctx.room, "name", "unknown"),
            "tool_count": len(all_tools),
        },
    )

    await session.generate_reply(instructions=reply_prompt)
    log_experiment_event(
        "initial_reply_generated",
        {
            "session_id": session_id,
            "user_id": user_id,
            "reply_prompt_length": len(reply_prompt),
        },
    )

    # ── Background Memory Extraction ──────────────────────────────────────────
    memory_extractor = MemoryExtractor()
    await memory_extractor.run(current_ctx)


# ─── CLI Entry Point ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Windows async policy fix
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    # Wait for valid LiveKit config (polling loop for browser-based setup)
    logger.info("Waiting for configuration...")
    while True:
        config.load_config()
        lk_url = config.get_api_key("livekit_url")
        lk_key = config.get_api_key("livekit_key")
        lk_secret = config.get_api_key("livekit_secret")

        if lk_url and lk_key and lk_secret:
            logger.info(f"Configuration found. Connecting to {lk_url}")
            logger.info(f"User: [{config.get_full_name()}] | ID: [{config.get_user_id()}]")

            os.environ["LIVEKIT_URL"] = lk_url
            os.environ["LIVEKIT_API_KEY"] = lk_key
            os.environ["LIVEKIT_API_SECRET"] = lk_secret

            google_key = config.get_api_key("google")
            openai_key = config.get_api_key("openai")
            mem0_key   = config.get_mem0_key()

            if google_key:
                os.environ["GOOGLE_API_KEY"] = google_key
            if openai_key:
                os.environ["OPENAI_API_KEY"] = openai_key
            if mem0_key:
                os.environ["MEM0_API_KEY"] = mem0_key
            else:
                logger.warning("Mem0 key not found — memory will use local JSON storage.")

            break
        else:
            logger.info("Config not ready — retrying in 2s...")
            time.sleep(2)

    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint, agent_name="Jarvis"))
