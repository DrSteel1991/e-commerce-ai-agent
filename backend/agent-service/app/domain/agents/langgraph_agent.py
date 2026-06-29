"""
LangGraph-based tool-calling agent (medium + long term).

Flow:
  customer message → LLM picks tool(s) → run tool(s) → LLM writes answer
  (repeats up to AGENT_MAX_TOOL_ITERATIONS for multi-step questions)
"""

import json
import logging
from typing import Literal, TypedDict

from app.domain.tools import AGENT_TOOLS, execute_tool, serialize_tool_result
from app.infrastructure.llm.openai_client import (
    MAX_TOOL_ITERATIONS,
    chat_completion_with_tools,
)
from langgraph.graph import END, StateGraph

logger = logging.getLogger(__name__)

AGENT_SYSTEM_PROMPT = """You are a helpful e-commerce customer support assistant.

You have tools to look up products, orders, and store policies.
Choose the best tool for each customer message. You may call multiple tools
in sequence for complex questions (e.g. find a product, then check return policy).

Rules:
- Use list_products when the customer wants to browse or see what you sell.
- Use search_products for specific keyword searches.
- Use search_products_semantic for vague or descriptive requests.
- Use get_order_status only when an order number is known; ask if missing.
- Use search_knowledge_base for refunds, shipping, payments, warranties, FAQs.
- Base your final answer ONLY on tool results. Do not invent data.
- Be concise and friendly. List products clearly when showing a catalog.
"""


class AgentState(TypedDict):
    messages: list
    user_id: str | None
    sources: list
    tools_used: list[str]
    data: dict | None
    iteration: int
    pending_tool_calls: list
    final_content: str | None


def _assistant_message_to_dict(message) -> dict:
    payload: dict = {"role": "assistant", "content": message.content or ""}
    if message.tool_calls:
        payload["tool_calls"] = [
            {
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                },
            }
            for tool_call in message.tool_calls
        ]
    return payload


async def call_model(state: AgentState) -> AgentState:
    message = chat_completion_with_tools(state["messages"], AGENT_TOOLS)
    messages = [*state["messages"], _assistant_message_to_dict(message)]

    return {
        **state,
        "messages": messages,
        "iteration": state["iteration"] + 1,
        "pending_tool_calls": list(message.tool_calls or []),
        "final_content": message.content,
    }


async def run_tools(state: AgentState) -> AgentState:
    tool_calls = state.get("pending_tool_calls") or []
    messages = list(state["messages"])
    tools_used = list(state["tools_used"])
    sources = list(state["sources"])
    data = state.get("data")

    for tool_call in tool_calls:
        name = tool_call.function.name
        try:
            arguments = json.loads(tool_call.function.arguments or "{}")
        except json.JSONDecodeError:
            arguments = {}

        result = await execute_tool(name, arguments, user_id=state["user_id"])
        tools_used.append(name)

        if name == "search_knowledge_base" and result.get("sources"):
            sources.extend(result["sources"])

        if "products" in result or "order" in result:
            data = result

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": serialize_tool_result(result),
            }
        )

    return {
        **state,
        "messages": messages,
        "tools_used": tools_used,
        "sources": sources,
        "data": data,
        "pending_tool_calls": [],
    }


def route_after_model(state: AgentState) -> Literal["tools", "done"]:
    if state.get("pending_tool_calls"):
        if state["iteration"] >= MAX_TOOL_ITERATIONS:
            logger.warning("Agent hit max tool iterations")
            return "done"
        return "tools"
    return "done"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("agent", call_model)
    graph.add_node("tools", run_tools)

    graph.set_entry_point("agent")
    graph.add_conditional_edges(
        "agent",
        route_after_model,
        {"tools": "tools", "done": END},
    )
    graph.add_edge("tools", "agent")

    return graph.compile()


_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


def _infer_intent(tools_used: list[str]) -> str:
    if not tools_used:
        return "general"

    last = tools_used[-1]
    mapping = {
        "list_products": "product_info",
        "search_products": "product_info",
        "search_products_semantic": "product_info",
        "get_order_status": "order_status",
        "search_knowledge_base": "policy",
    }
    return mapping.get(last, "general")


def _build_agent_action(tools_used: list[str], iteration: int) -> str:
    if not tools_used:
        return "tool_agent_direct"
    if len(tools_used) == 1:
        return f"tool_{tools_used[0]}"
    return f"tool_agent_multi_step_{len(tools_used)}"


async def run_tool_agent(
    message: str,
    *,
    user_id: str | None,
    history: list[dict[str, str]],
) -> dict:
    """Run the LangGraph tool-calling agent for one customer turn."""
    messages: list = [
        {"role": "system", "content": AGENT_SYSTEM_PROMPT},
        *history,
        {"role": "user", "content": message},
    ]

    initial_state: AgentState = {
        "messages": messages,
        "user_id": user_id,
        "sources": [],
        "tools_used": [],
        "data": None,
        "iteration": 0,
        "pending_tool_calls": [],
        "final_content": None,
    }

    final_state = await get_graph().ainvoke(initial_state)

    answer = final_state.get("final_content")
    if not answer:
        answer = (
            "I wasn't able to complete that request. "
            "Could you rephrase or provide more details?"
        )

    tools_used: list[str] = final_state.get("tools_used", [])

    return {
        "answer": answer,
        "sources": final_state.get("sources", []),
        "agent_action": _build_agent_action(tools_used, final_state["iteration"]),
        "intent": _infer_intent(tools_used),
        "user_id": user_id,
        "data": final_state.get("data"),
    }
