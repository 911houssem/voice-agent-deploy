import json
from pathlib import Path

def load_json(path: Path):
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path: Path, data: dict):
    with path.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
