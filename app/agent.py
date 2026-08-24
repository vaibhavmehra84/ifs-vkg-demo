import os
import json
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from app.database import graph_edges_col
from app.mock_cots import mock_cots_api_router

# State Schema
class AgentState(TypedDict):
    employee_id: str
    target_rank: str
    discovered_routes: List[Dict[str, Any]]
    fetched_cots_payloads: Dict[str, Any]
    evaluation_result: str

# LLM Setup
llm = ChatAnthropic(
    model="claude-sonnet-4-5",
    temperature=0,
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Nodes
def discover_routes_node(state: AgentState) -> Dict[str, Any]:
    """Queries MongoDB VKG Store for all valid COTS API routes related to CrewMember."""
    routes = list(graph_edges_col.find(
        {"sourceEntityType": "CrewMember"},
        {"_id": 0}
    ))
    return {"discovered_routes": routes}

def fetch_cots_data_node(state: AgentState) -> Dict[str, Any]:
    """Executes Just-In-Time API calls to mock COTS backends discovered via VKG."""
    emp_id = state["employee_id"]
    routes = state["discovered_routes"]
    payloads = {}

    for route in routes:
        provider = route["cotsProvider"]
        pattern = route["endpointPattern"]
        # Use edgeId or combine provider + target entity to prevent key overwriting
        payload_key = route.get("edgeId", f"{provider}_{route['targetEntityType']}")
        
        data = mock_cots_api_router(pattern, emp_id)
        payloads[payload_key] = data

    return {"fetched_cots_payloads": payloads}

def evaluate_candidate_node(state: AgentState) -> Dict[str, Any]:
    """Uses Claude to reason over aggregated JIT data for promotion decisions."""
    prompt = f"""
    You are an AI Promotion Assessor for an airline's In-Flight Services (IFS) department.
    Evaluate candidate '{state['employee_id']}' for promotion to '{state['target_rank']}'.

    Below is live payload data fetched dynamically from disparate COTS systems via Virtual Knowledge Graph routing:
    {json.dumps(state['fetched_cots_payloads'], indent=2)}

    Evaluation Rules:
    1. Minimum Service Years: 5.0 years
    2. Active Disciplinary Warnings: Must be 0
    3. Minimum Appreciations: At least 10
    4. On-Time Performance (OTP): At least 98.0%

    Provide your verdict in Markdown containing:
    - Candidate Status (RECOMMENDED or NOT RECOMMENDED)
    - Detailed Breakdown against each rule using source COTS references
    - Final Summary Recommendation
    """
    response = llm.invoke(prompt)
    return {"evaluation_result": response.content}

# LangGraph Build
workflow = StateGraph(AgentState)
workflow.add_node("discover_routes", discover_routes_node)
workflow.add_node("fetch_cots_data", fetch_cots_data_node)
workflow.add_node("evaluate_candidate", evaluate_candidate_node)

workflow.set_entry_point("discover_routes")
workflow.add_edge("discover_routes", "fetch_cots_data")
workflow.add_edge("fetch_cots_data", "evaluate_candidate")
workflow.add_edge("evaluate_candidate", END)

vkg_agent_app = workflow.compile()