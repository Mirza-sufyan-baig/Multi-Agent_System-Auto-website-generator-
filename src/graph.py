from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from .nodes import manager_node, architect_node, developer_node, deployer_node

class AgentState(TypedDict):
    messages: List[Dict[str, str]]
    user_input: str
    requirements: str
    workspace_path: str
    project_id: str
    plan_content: str
    tasks: List[str]
    completed_tasks: List[str]
    deployment_url: str
    status: str
    error: str
    fix_request: Optional[str]   # <--- NEW: Stores the immediate fix instruction
    retry_count: int             # <--- NEW: Prevents infinite loops

def route_manager(state):
    # If we are just starting building
    if state["status"] in ["EXECUTION", "EDITING"]:
        return "architect"
    # If we are done and manager just reported success
    if state["status"] == "FINISHED":
        return END
    return END

def route_developer(state):
    # If there are still tasks in the queue
    if state.get("tasks") and len(state["tasks"]) > 0:
        return "developer"
    # If queue is empty, try to deploy
    return "deployer"

def route_deployer(state):
    # If Deployer found an issue, send back to Developer
    if state.get("status") == "NEEDS_FIX":
        return "developer"
    # If success, send to Manager to announce it
    if state.get("status") == "DONE":
        return "manager"
    return END

def create_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("manager", manager_node)
    workflow.add_node("architect", architect_node)
    workflow.add_node("developer", developer_node)
    workflow.add_node("deployer", deployer_node)
    
    workflow.set_entry_point("manager")
    
    workflow.add_conditional_edges("manager", route_manager)
    workflow.add_edge("architect", "developer")
    workflow.add_conditional_edges("developer", route_developer)
    
    # Deployer decides: Fix again? or Tell Manager it's done?
    workflow.add_conditional_edges(
        "deployer", 
        route_deployer,
        {
            "developer": "developer", 
            "manager": "manager"
        }
    )
    
    return workflow.compile()