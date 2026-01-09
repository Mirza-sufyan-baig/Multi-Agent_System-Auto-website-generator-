import json
import re
from typing import Any, Dict
from .base import BaseAgent
from ..prompts import MANAGER_PROMPT

class ManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__("Manager")

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        history = input_data.get("messages", [])
        user_input = input_data.get("user_input", "")
        deployment_url = input_data.get("deployment_url", "")
        # EXISTING requirements to prevent amnesia
        existing_reqs = input_data.get("requirements", "") 
        
        system_content = MANAGER_PROMPT
        if deployment_url:
            system_content += f"\n\nCURRENT STATUS: The site is DEPLOYED at {deployment_url}."
        else:
            system_content += f"\n\nCURRENT STATUS: The site is NOT built yet."

        messages = [{"role": "system", "content": system_content}]
        messages.extend(history[-6:])
        messages.append({"role": "user", "content": f"User Input: {user_input}"})

        try:
            response = self.llm.invoke(messages)
            content = response.content
            
            # --- ROBUST JSON EXTRACTION (Regex method is safer) ---
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
            else:
                raise ValueError("No JSON found")
            
            # --- CONTEXT MERGING ---
            # If status is EDITING, we append to history, we don't replace it completely
            # unless the LLM explicitly summarized everything perfectly.
            # A simple heuristic: Keep old reqs if they aren't mentioned?
            # For now, let's append new intent to old reqs for safety
            if existing_reqs and data["status"] == "EDITING":
                data["requirements"] = f"Original: {existing_reqs}\nUpdate: {data['requirements']}"

            return data
            
        except Exception as e:
            print(f"Manager Parse Error: {e} | Content: {content[:50]}...")
            # Fallback
            return {
                "response": "I'm on it.", 
                "status": "EXECUTION", 
                "requirements": user_input
            }