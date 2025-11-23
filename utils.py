# utils.py
import re
from pathlib import Path

def safe_filename(s: str) -> str:
    s = s.strip().replace(" ", "_")
    return re.sub(r'(?u)[^-\w.]', '', s)

def ensure_data_dir():
    p = Path("data")
    p.mkdir(parents=True, exist_ok=True)
    return p
