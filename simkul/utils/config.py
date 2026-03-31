import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".simkul"
CONFIG_FILE = CONFIG_DIR / "config.json"

def _ensure_dir():
    """Pastikan folder ~/.simkul ada."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def _read_config() -> dict:
    """Baca isi config.json."""
    _ensure_dir()
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def _write_config(data: dict):
    """Tulis data ke config.json."""
    _ensure_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get(key: str, default=None):
    """Ambil nilai dari config berdasarkan key."""
    return _read_config().get(key, default)

def set(key: str, value):
    """Simpan nilai ke config berdasarkan key."""
    config = _read_config()
    config[key] = value
    _write_config(config)

def delete(key: str):
    """Hapus key dari config."""
    config = _read_config()
    config.pop(key, None)
    _write_config(config)

def clear():
    """Hapus semua isi config."""
    _write_config({})