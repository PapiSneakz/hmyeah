
import os
from datetime import datetime

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def ts_to_str(ts_ms: int) -> str:
    return datetime.utcfromtimestamp(ts_ms/1000).strftime('%Y-%m-%d %H:%M:%S')
