import json
from pathlib import Path
from datetime import datetime, timedelta

SESSION_FILE = Path.home() / ".simkul" / "session.json"

def save_session(cookies: list, npm: str):
    """Simpan cookies dan waktu expire ke file."""
    data = {
        "npm": npm,
        "cookies": cookies,
        "saved_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(hours=8)).isoformat(),
    }
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_session() -> dict | None:
    """Load session dari file. Return None kalau tidak ada atau sudah expired."""
    if not SESSION_FILE.exists():
        return None

    with open(SESSION_FILE, "r") as f:
        data = json.load(f)

    expires_at = datetime.fromisoformat(data["expires_at"])
    if datetime.now() > expires_at:
        delete_session()
        return None

    return data

def delete_session():
    """Hapus session (untuk logout)."""
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()

def is_logged_in() -> bool:
    """Cek apakah session masih valid."""
    return load_session() is not None