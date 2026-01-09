import os
import json
import socket
import shutil

def find_free_port(start_port=8001):
    """Find a free port starting from 8001."""
    port = start_port
    while port < 65535:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) != 0:
                return port
        port += 1
    raise RuntimeError("No free ports found")

def get_project_state(project_id: str) -> dict:
    """Load state from JSON."""
    path = f"workspace/{project_id}/state.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None
    return None

def save_project_state(project_id: str, state: dict):
    """Save state to JSON (exclude non-serializable)."""
    path = f"workspace/{project_id}/state.json"
    clean_state = {k: v for k, v in state.items() if k not in ['messages_object']}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(clean_state, f, indent=2, ensure_ascii=False)

def save_chat_history(project_id: str, messages: list):
    path = f"workspace/{project_id}/chat.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)

def load_chat_history(project_id: str) -> list:
    path = f"workspace/{project_id}/chat.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []