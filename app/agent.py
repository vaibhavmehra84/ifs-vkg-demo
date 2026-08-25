import os
from typing import Annotated, TypedDict, List
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from app.database import (
    graph_edges_col,
    cots_successfactors_col,
    cots_aims_otp_col,
    cots_ifs_appreciations_col,
    cots_ifs_warnings_col
)

# -----------------------------------------------------------------------------
# 1. Dynamic VKG & COTS Tools
# -----------------------------------------------------------------------------

@tool
def discover_vkg_routes(query_intent: str) -> list:
    """Queries MongoDB metadata edges to find relevant API endpoints and schema classes for a user intent."""
    # Matches edges dynamically based on keywords or vector search
    routes = list(graph_edges_col.find({
        "$or": [
            {"description": {"$regex": query_intent, "$options": "i"}},
            {"targetEntityType": {"$regex": query_intent, "$options": "i"}}
        ]
    }, {"_id": 0}))
    return routes if routes else list(graph_edges_col.find({}, {"_id": 0}))

@tool
def query_crew_by_base(base_code: str) -> list:
    """Finds all crew members assigned to a specific base location (e.g., 'BOM', 'DEL', 'BLR')."""
    return list(cots_successfactors_col.find(
        {"baseLocation": {"$regex": base_code, "$options": "i"}},
        {"_id": 0}
    ))

@tool
def fetch_full_crew_profile(employee_id: str) -> dict:
    """Fetches combined operational data across SuccessFactors, AIMS OTP, Appreciations, and Warnings for a specific crew member."""
    return {
        "hr_profile": cots_successfactors_col.find_one({"_id": employee_id}, {"_id": 0}) or {},
        "flight_ops": cots_aims_otp_col.find_one({"_id": employee_id}, {"_id": 0}) or {},
        "appreciations": cots_ifs_appreciations_col.find_one({"_id": employee_id}, {"_id": 0}) or {},
        "warnings": cots_ifs_warnings_col.find_one({"_id": employee_id}, {"_id": 0}) or {}
    }

tools = [discover_vkg_routes, query_crew_by_base, fetch_full_crew_profile]

# -----------------------------------------------------------------------------
# 2. Conversational Agent Graph
# -----------------------------------------------------------------------------

class ChatState(TypedDict):
    messages: Annotated[list, add_messages]

llm = ChatAnthropic(
    model="claude-sonnet-4-5",
    temperature=0,
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
).bind_tools(tools)

def agent_node(state: ChatState):
    system_prompt = (
        "You are an AI Flight Operations & HR Assistant powered by a Virtual Knowledge Graph (VKG).\n"
        "You have tools to search schema edges, query crew by base location, and fetch full performance profiles.\n"
        "For complex queries (e.g., ranking top crew in Bombay or generating business cases), use your tools "
        "to gather data from COTS systems first before forming your final response.\n"
        "CRITICAL: Before making any tool calls, briefly state your reasoning and plan (e.g., why you are choosing a specific tool or querying a specific COTS database)."
    )
    messages = [{"role": "system", "content": system_prompt}] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

# Build Graph
builder = StateGraph(ChatState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools))

builder.set_entry_point("agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")

vkg_conversational_agent = builder.compile()