import os
import threading
import uuid
from dataclasses import dataclass, field

from dotenv import load_dotenv

_ = load_dotenv()

MAX_MESSAGES = int(os.environ.get("CONVERSATION_MAX_MESSAGES", "20"))


@dataclass
class ConversationMessage:
    role: str
    content: str


@dataclass
class ConversationStore:
    sessions: dict[str, list[ConversationMessage]] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)


_store = ConversationStore()


def ensure_session_id(session_id: str | None) -> str:
    return session_id or str(uuid.uuid4())


def get_history(session_id: str, *, limit: int = 10) -> list[dict[str, str]]:
    with _store.lock:
        messages = _store.sessions.get(session_id, [])

    recent = messages[-limit:]
    return [{"role": message.role, "content": message.content} for message in recent]


def append_message(session_id: str, role: str, content: str) -> None:
    with _store.lock:
        if session_id not in _store.sessions:
            _store.sessions[session_id] = []

        _store.sessions[session_id].append(
            ConversationMessage(role=role, content=content)
        )

        if len(_store.sessions[session_id]) > MAX_MESSAGES:
            _store.sessions[session_id] = _store.sessions[session_id][-MAX_MESSAGES:]


def clear_session(session_id: str) -> None:
    with _store.lock:
        _store.sessions.pop(session_id, None)
