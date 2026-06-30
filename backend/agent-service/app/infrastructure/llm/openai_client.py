import os
from collections.abc import Iterable

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam

_ = load_dotenv()

OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
MAX_TOOL_ITERATIONS = int(os.environ.get("AGENT_MAX_TOOL_ITERATIONS", "5"))
_client: OpenAI | None = None


def is_llm_available() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY"))


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _client


def chat_completion_with_tools(
    messages: Iterable[ChatCompletionMessageParam],
    tools: Iterable[ChatCompletionToolParam],
    *,
    temperature: float = 0,
):
    """Call OpenAI with tool definitions; returns the assistant message object."""
    response = get_client().chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        tools=tools,
        temperature=temperature,
    )
    return response.choices[0].message
