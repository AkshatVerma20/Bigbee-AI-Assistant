import requests
import json
from typing import Generator


class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def chat(self, message: str, user_id: str, session_id: str) -> str:
        resp = requests.post(
            f"{self.base_url}/api/chat",
            json={"message": message, "user_id": user_id, "session_id": session_id, "stream": False},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["response"]

    def chat_stream(self, message: str, user_id: str, session_id: str) -> Generator[str, None, None]:
        """Yields response tokens as they arrive via SSE."""
        with requests.post(
            f"{self.base_url}/api/chat",
            json={"message": message, "user_id": user_id, "session_id": session_id, "stream": True},
            stream=True,
            timeout=120,
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if line and line.startswith(b"data: "):
                    try:
                        data = json.loads(line[6:])
                        if data.get("done"):
                            break
                        if "error" in data:
                            yield f"\n\n⚠️ {data['error']}"
                            break
                        token = data.get("token", "")
                        if token:
                            yield token
                    except json.JSONDecodeError:
                        pass

    def upload_file(self, file_bytes: bytes, filename: str, content_type: str) -> dict:
        resp = requests.post(
            f"{self.base_url}/api/upload",
            files={"file": (filename, file_bytes, content_type)},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()

    def get_history(self, user_id: str, session_id: str) -> list:
        resp = requests.get(
            f"{self.base_url}/api/history/{user_id}/{session_id}",
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get("messages", [])

    def clear_history(self, user_id: str, session_id: str):
        requests.delete(
            f"{self.base_url}/api/history/{user_id}/{session_id}",
            timeout=15,
        )

    def list_uploads(self) -> list:
        try:
            resp = requests.get(f"{self.base_url}/api/uploads", timeout=10)
            return resp.json().get("files", [])
        except Exception:
            return []

    def multi_agent(self, task: str, user_id: str = "default") -> dict:
        resp = requests.post(
            f"{self.base_url}/api/multi-agent",
            json={"task": task, "user_id": user_id},
            timeout=180,
        )
        resp.raise_for_status()
        return resp.json()

    def health(self) -> bool:
        try:
            return requests.get(f"{self.base_url}/health", timeout=5).ok
        except Exception:
            return False
