import threading
import subprocess
import os
from typing import Any, Dict
from .base import BaseAgent
from ..utils import find_free_port

SERVER_REGISTRY = {}

class DeployerAgent(BaseAgent):
    def __init__(self):
        super().__init__("Deployer")

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        workspace = input_data.get("workspace_path")
        project_id = input_data.get("project_id")
        
        # --- 1. VALIDATION (The "Quality Gate") ---
        # We assume index.html is the entry point. 
        # In a real app, we might check parsing errors, but existence is key for MVP.
        required_files = ["index.html"]
        missing = []
        
        if os.path.exists(workspace):
            existing_files = os.listdir(workspace)
            for f in required_files:
                if f not in existing_files:
                    missing.append(f)
                elif os.path.getsize(os.path.join(workspace, f)) == 0:
                    missing.append(f"{f} (File is empty)")
        else:
            missing = ["Workspace folder not found"]

        # If validation fails, return instruction for Developer
        if missing:
            error_msg = f"Critical Deployment Error: The following files are missing or empty: {', '.join(missing)}."
            print(f"🛑 [Deployer] Validation Failed: {error_msg}")
            return {
                "status": "NEEDS_FIX",
                "fix_request": f"URGENT: {error_msg} Create these files immediately based on the Plan.",
                "url": ""
            }

        # --- 2. DEPLOYMENT (Only if Valid) ---
        if project_id in SERVER_REGISTRY:
            return {"url": SERVER_REGISTRY[project_id], "status": "SUCCESS"}
            
        try:
            port = find_free_port()
            
            def start_server():
                subprocess.run(
                    ["python", "-m", "http.server", str(port)],
                    cwd=workspace,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            t = threading.Thread(target=start_server, daemon=True)
            t.start()
            
            url = f"http://localhost:{port}"
            SERVER_REGISTRY[project_id] = url
            return {"url": url, "status": "SUCCESS"}
            
        except Exception as e:
            # If port fails, that's a system error, not a code error.
            return {"url": "", "status": "FAILED", "error": str(e)}