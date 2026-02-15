import json
import hashlib
import secrets
from pathlib import Path
from typing import Any

def generate_salt() -> str:
    # Генерация случайной соли
    return secrets.token_hex(8)

def hash_password(password: str, salt: str) -> str:
    # Хеширование пароля с использованием соли
    data = (password + salt).encode("utf-8")
    return hashlib.sha256(data).hexdigest()

def load_json(path: Path, default: Any) -> Any:
    # Безопасная загрузка JSON
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default

def save_json(path: Path, data: Any) -> None:
    # Безопасное сохранение JSON
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp_path.replace(path)