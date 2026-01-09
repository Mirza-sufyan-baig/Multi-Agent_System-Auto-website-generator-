from typing import Dict, Any
from .agents.manager import ManagerAgent
from .agents.architect import ArchitectAgent
from .agents.developer import DeveloperAgent
from .agents.deployer import DeployerAgent

def manager_node(state):
    print("💬 Manager Node")
    agent = ManagerAgent()
    
    # If we are coming back from Deployment Success
    if state.get("status") == "DONE":
        url = state.get("deployment_url")
        # We manually construct a success message context
        user_input_mock = f"The site is successfully deployed at {url}. Tell the user it is ready."
        res = agent.run({
        "user_input": state["user_input"],
        "messages": state.get("messages", []),
        "deployment_url": state.get("deployment_url", ""),
        "requirements": state.get("requirements", "")
    })
        
        new_msgs = state.get("messages", [])
        new_msgs.append({"role": "user", "content": state["user_input"]})
        new_msgs.append({"role": "assistant", "content": res["response"]})
        
        return {
            "messages": new_msgs,
            "status": res["status"],
            "requirements": res.get("requirements", ""),
            "retry_count": 0
        }

    # Normal Flow
    res = agent.run({
        "user_input": state["user_input"],
        "messages": state.get("messages", []),
        "deployment_url": state.get("deployment_url", "")
    })
    
    new_msgs = state.get("messages", [])
    new_msgs.append({"role": "user", "content": state["user_input"]})
    new_msgs.append({"role": "assistant", "content": res["response"]})
    
    return {
        "messages": new_msgs,
        "status": res["status"],
        "requirements": res.get("requirements", state.get("requirements", "")),
        "retry_count": 0 # Reset retries on new input
    }

def architect_node(state):
    print("🏗️ Architect Node")
    agent = ArchitectAgent()
    res = agent.run({
        "requirements": state["requirements"],
        "workspace_path": state["workspace_path"]
    })
    return {
        "plan_content": res["plan_content"],
        "tasks": res["tasks"],
        "status": "DEVELOPMENT"
    }

def developer_node(state):
    print("💻 Developer Node")
    agent = DeveloperAgent()
    
    # PRIORITY CHECK: Is there a Fix Request from Deployer?
    fix_request = state.get("fix_request")
    retries = state.get("retry_count", 0)
    
    if fix_request:
        if retries > 3:
            print("❌ Too many retries. Aborting.")
            return {"status": "ERROR", "error": "Unable to fix deployment issues after 3 attempts."}

        print(f"🚨 [Developer] Handling Urgent Fix: {fix_request}")
        
        # We run the agent specifically on the fix
        res = agent.run({
            "task": fix_request, # The "Task" is the error message
            "plan_context": state.get("plan_content", ""),
            "workspace_path": state["workspace_path"]
        })
        
        # Clear the request and increment retry
        return {
            "fix_request": None,
            "retry_count": retries + 1,
            "status": "DEVELOPMENT" # Go back to Deployer via conditional edge
        }

    # Normal Task Flow
    tasks = state.get("tasks", [])
    completed = state.get("completed_tasks", [])
    
    if not tasks:
        return {"status": "DEPLOYMENT_READY"}
        
    current_task = tasks[0]
    
    res = agent.run({
        "task": current_task,
        "plan_context": state.get("plan_content", ""),
        "workspace_path": state["workspace_path"]
    })
    
    return {
        "tasks": tasks[1:],
        "completed_tasks": completed + [current_task],
        "status": "DEVELOPMENT"
    }

def deployer_node(state):
    print("🚀 Deployer Node")
    agent = DeployerAgent()
    
    res = agent.run({
        "workspace_path": state["workspace_path"],
        "project_id": state["project_id"]
    })
    
    # If Deployer requests a fix
    if res["status"] == "NEEDS_FIX":
        return {
            "status": "NEEDS_FIX",
            "fix_request": res["fix_request"]
        }
        
    # If System Error
    if res["status"] == "FAILED":
        return {
            "status": "ERROR",
            "error": res.get("error")
        }
        
    # Success
    return {
        "deployment_url": res["url"],
        "status": "DONE",
        "error": "",
        "fix_request": None
    }