import subprocess
from simkul.utils.config import get as config_get, set as config_set


def kirim_notif(tipe: str, judul: str, pesan: str):
    """
    Kirim push notification via ntfy.sh.
    tipe: "sukses" | "info" | "error"
    """
    topic = config_get("ntfy_topic")
    if not topic:
        # Notifikasi dinonaktifkan, skip
        return

    topic_map = {
        "sukses": f"{topic}-sukses",
        "info": f"{topic}-info",
        "error": f"{topic}-error",
    }

    url = f"ntfy.sh/{topic_map.get(tipe, topic)}"

    try:
        subprocess.run(
            ["curl", "-H", f"Title: {judul}", "-d", pesan, url],
            capture_output=True,
            timeout=10,
        )
    except Exception:
        # Notifikasi gagal tidak boleh crash program utama
        pass


def setup_notif():
    """
    Interaktif setup topic ntfy — dipanggil dari command simkul config.
    """
    from InquirerPy import inquirer
    from rich.console import Console

    console = Console()

    console.print("\n[bold]Setup Notifikasi (ntfy.sh)[/bold]")
    console.print("[dim]Kosongkan untuk menonaktifkan notifikasi.[/dim]\n")

    topic = inquirer.text(
        message="Masukkan nama topic ntfy kamu (contoh: akbar-simkul):",
    ).execute()

    if topic.strip():
        config_set("ntfy_topic", topic.strip())
        console.print(f"\n[green]✓ Topic ntfy disimpan: {topic.strip()}[/green]")
        console.print(f"[dim]Subscribe ke topic berikut di app ntfy:[/dim]")
        console.print(f"  [cyan]{topic}-sukses[/cyan]")
        console.print(f"  [cyan]{topic}-info[/cyan]")
        console.print(f"  [cyan]{topic}-error[/cyan]")
    else:
        config_set("ntfy_topic", "")
        console.print("\n[yellow]Notifikasi dinonaktifkan.[/yellow]")