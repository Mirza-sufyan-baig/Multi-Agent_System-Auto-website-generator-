from typing import Any, Dict
import re
from .base import BaseAgent
from ..prompts import ARCHITECT_PROMPT
from ..tools import FileTool

class ArchitectAgent(BaseAgent):
    def __init__(self):
        super().__init__("Architect")

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        requirements = input_data.get("requirements", "")
        workspace_path = input_data.get("workspace_path")
        
        msg = [
            {"role": "system", "content": ARCHITECT_PROMPT},
            {"role": "user", "content": f"Requirements:\n{requirements}"}
        ]
        
        response = self.llm.invoke(msg)
        plan = response.content
        
        # Save Plan
        FileTool.write_file(f"{workspace_path}/plan.md", plan)
        
        # Extract Tasks using Strict Block
        tasks = []
        if "---TASKS---" in plan and "---END_TASKS---" in plan:
            task_block = plan.split("---TASKS---")[1].split("---END_TASKS---")[0]
            for line in task_block.split("\n"):
                if "- [ ]" in line:
                    tasks.append(line.replace("- [ ]", "").strip())
        else:
            # Fallback
            for line in plan.split("\n"):
                if line.strip().startswith("- [ ]"):
                    tasks.append(line.replace("- [ ]", "").strip())
        
        # Fallback 2: If no tasks found, assume index.html creation
        if not tasks:
            tasks = ["Create index.html based on the plan"]
            
        return {"plan_content": plan, "tasks": tasks, "workspace_path": workspace_path}