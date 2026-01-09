import os

class FileTool:
    @staticmethod
    def write_file(path: str, content: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Written to {path}"

    @staticmethod
    def read_file(path: str) -> str:
        if not os.path.exists(path): return ""
        with open(path, "r", encoding="utf-8") as f:
            return f.read()