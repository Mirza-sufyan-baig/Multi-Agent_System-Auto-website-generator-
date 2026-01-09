import re
import os
from typing import Any, Dict
from .base import BaseAgent
from ..prompts import DEVELOPER_PROMPT
from ..tools import FileTool

class DeveloperAgent(BaseAgent):
    def __init__(self):
        super().__init__("Developer")

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        task = input_data.get("task", "")
        plan = input_data.get("plan_context", "")
        workspace = input_data.get("workspace_path", "")
        
        # Context Awareness: Read all HTML/CSS/JS files
        context = ""
        for f in os.listdir(workspace):
            if f.endswith(('.html', '.css', '.js')):
                content = FileTool.read_file(os.path.join(workspace, f))
                context += f"\n--- {f} ---\n{content}\n"
        
        msg = [
            {"role": "system", "content": DEVELOPER_PROMPT},
            {"role": "user", "content": f"PLAN:\n{plan}\n\nEXISTING FILES:\n{context}\n\nTASK:\n{task}"}
        ]
        
        response = self.llm.invoke(msg)
        content = response.content
        
        # Robust Parsing
        files_created = []
        
        # Regex 1: Explicit FILE: format
        matches = re.findall(r"FILE:\s*([^\n]+)\n```(\w+)?\n(.*?)```", content, re.DOTALL)
        
        if not matches:
            # Regex 2: Loose code blocks
            blocks = re.findall(r"```(\w+)?\n(.*?)```", content, re.DOTALL)
            for lang, code in blocks:
                if lang in ['html', 'css', 'javascript', 'js']:
                    filename = "index.html" if lang == 'html' else ("script.js" if lang in ['js', 'javascript'] else "style.css")
                    matches.append((filename, lang, code))
        
        for filename, _, code in matches:
            filename = filename.strip()
            path = os.path.join(workspace, filename)
            FileTool.write_file(path, code.strip())
            files_created.append(filename)
            
        return {"files": files_created}