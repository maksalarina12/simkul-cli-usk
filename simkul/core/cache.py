import json
from pathlib import Path
from datetime import datetime

CACHE_DIR = Path.home() / ".simkul"
JADWAL_CACHE_FILE = CACHE_DIR / "jadwal_cache.json"


def save_jadwal_cache(jadwal: list[dict]):
    """Simpan jadwal semester ke cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "scraped_at": datetime.now().isoformat(),
        "jadwal": jadwal,
    }
    with open(JADWAL_CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


def load_jadwal_cache() -> list[dict] | None:
    """Load jadwal dari cache. Return None kalau belum ada."""
    if not JADWAL_CACHE_FILE.exists():
        return None
    with open(JADWAL_CACHE_FILE, "r") as f:
        data = json.load(f)
    return data.get("jadwal")


def get_cache_info() -> dict | None:
    """Return info cache (scraped_at, jumlah MK). None kalau belum ada."""
    if not JADWAL_CACHE_FILE.exists():
        return None
    with open(JADWAL_CACHE_FILE, "r") as f:
        data = json.load(f)
    return {
        "scraped_at": data.get("scraped_at"),
        "jumlah": len(data.get("jadwal", [])),
    }


def delete_jadwal_cache():
    """Hapus cache jadwal."""
    if JADWAL_CACHE_FILE.exists():
        JADWAL_CACHE_FILE.unlink()