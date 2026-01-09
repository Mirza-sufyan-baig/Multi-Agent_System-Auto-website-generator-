import os
import sys
import json
import asyncio
import time
import random
import string
import shutil
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

# --- CONFIGURATION ---
ENABLE_TRACING = False # <--- SET THIS TO TRUE TO ENABLE LANGFUSE
# ---------------------

# Fix encoding for Windows
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# Set env var for llm_factory to pick up
if ENABLE_TRACING:
    os.environ["LANGFUSE_ENABLED"] = "true"
else:
    os.environ["LANGFUSE_ENABLED"] = "false"

from src.graph import create_graph
from src.utils import load_chat_history, save_chat_history, get_project_state, save_project_state
from src.llm_factory import llm_factory

app = FastAPI(title="AutoDev Studio")

# Create directories
os.makedirs("static", exist_ok=True)
os.makedirs("workspace", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Thread pool for running blocking graph operations
executor = ThreadPoolExecutor(max_workers=5)

sessions: Dict[WebSocket, dict] = {}

def generate_project_id() -> str:
    """Generate unique project ID."""
    adjectives = ["super", "fast", "mega", "hyper", "auto", "smart"]
    nouns = ["site", "app", "web", "dev", "build", "stack"]
    suffix = ''.join(random.choices(string.digits, k=3))
    return f"{random.choice(adjectives)}-{random.choice(nouns)}-{suffix}"

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/api/projects")
async def list_projects():
    projects = []
    if os.path.exists("workspace"):
        dirs = [d for d in os.listdir("workspace") if os.path.isdir(os.path.join("workspace", d))]
        dirs.sort(key=lambda x: os.path.getmtime(os.path.join("workspace", x)), reverse=True)
        for name in dirs:
            state = get_project_state(name)
            status = state.get("status", "new") if state else "new"
            projects.append({"name": name, "status": status})
    return {"projects": projects}

@app.post("/api/projects/new")
async def create_project():
    new_project = generate_project_id()
    project_path = os.path.join("workspace", new_project)
    os.makedirs(project_path, exist_ok=True)
    return {"project": new_project}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    sessions[websocket] = {"project_id": "", "building": False}
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "select_project":
                project_id = data["project"]
                sessions[websocket]["project_id"] = project_id
                history = load_chat_history(project_id)
                
                await websocket.send_json({"type": "clear_chat"})
                for msg in history:
                    msg_type = "user_message" if msg["role"] == "user" else "assistant_message"
                    await websocket.send_json({"type": msg_type, "content": msg["content"]})
                
                state = get_project_state(project_id)
                if state and state.get("deployment_url"):
                    await websocket.send_json({"type": "deployed", "url": state["deployment_url"]})
                await websocket.send_json({"type": "log", "message": f"📂 Loaded project: {project_id}"})

            elif data["type"] == "message":
                user_input = data["content"]
                project_id = sessions[websocket]["project_id"]
                
                if not project_id:
                    project_id = generate_project_id()
                    sessions[websocket]["project_id"] = project_id
                    os.makedirs(os.path.join("workspace", project_id), exist_ok=True)
                    await websocket.send_json({"type": "project_created", "project": project_id})

                await websocket.send_json({"type": "user_message", "content": user_input})
                
                if sessions[websocket]["building"]:
                    await websocket.send_json({"type": "assistant_message", "content": "🔒 Busy building..."})
                    continue

                current_state = get_project_state(project_id)
                if not current_state:
                    current_state = {
                        "messages": [], "status": "DISCOVERY", "user_input": "", "requirements": "",
                        "workspace_path": f"workspace/{project_id}", "project_id": project_id,
                        "tasks": [], "completed_tasks": [], "plan_content": "", "deployment_url": "", "error": ""
                    }
                
                current_state["user_input"] = user_input
                sessions[websocket]["building"] = True
                await websocket.send_json({"type": "log", "message": "🧠 Thinking..."})
                
                loop = asyncio.get_event_loop()
                try:
                    app_graph = create_graph()
                    # Run Graph
                    final_state = await loop.run_in_executor(executor, app_graph.invoke, current_state)
                    
                    save_project_state(project_id, final_state)
                    save_chat_history(project_id, final_state.get("messages", []))
                    
                    last_msg = ""
                    for m in reversed(final_state.get("messages", [])):
                        if m["role"] == "assistant":
                            last_msg = m["content"]
                            break
                    
                    await websocket.send_json({"type": "assistant_message", "content": last_msg or "Done."})
                    
                    if final_state.get("status") == "FINISHED":
                        url = final_state.get("deployment_url")
                        await websocket.send_json({"type": "deployed", "url": url, "project": project_id})
                    
                    if final_state.get("error"):
                         await websocket.send_json({"type": "error", "message": final_state["error"]})

                except Exception as e:
                    print(f"Graph Error: {e}")
                    import traceback
                    traceback.print_exc()
                    await websocket.send_json({"type": "error", "message": str(e)})
                finally:
                    sessions[websocket]["building"] = False
                    await websocket.send_json({"type": "build_complete"})

    except WebSocketDisconnect:
        if websocket in sessions:
            del sessions[websocket]

if __name__ == "__main__":
    print(f"🚀 AutoDev Studio (Tracing: {ENABLE_TRACING})")
    print("📍 http://localhost:3000")
    uvicorn.run(app, host="0.0.0.0", port=3000, log_level="warning")