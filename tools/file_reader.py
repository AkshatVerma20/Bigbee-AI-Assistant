from langchain_core.tools import tool
from backend.config import settings
import os


@tool
def file_reader(filename: str) -> str:
    """Read the contents of an uploaded file by filename.
    Only works for files that have been uploaded via the /upload endpoint.
    Input: just the filename (e.g. 'report.txt'), not a full path.
    """
    safe_path = os.path.join(settings.upload_dir, os.path.basename(filename))
    if not os.path.exists(safe_path):
        return f"File '{filename}' not found. Please upload it first via the sidebar."
    try:
        with open(safe_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(8000)
        return f"Contents of {filename}:\n\n{content}"
    except Exception as e:
        return f"Error reading '{filename}': {e}"
