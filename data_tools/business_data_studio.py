from __future__ import annotations


import traceback
from pathlib import Path


def _show_startup_error(details: str, log_path: Path) -> None:
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Business Data Automation Studio",
            (
                "Uygulama başlatılamadı.\n\n"
                f"Hata ayrıntıları şu dosyaya kaydedildi:\n{log_path}\n\n"
                "Bu dosyayı paylaşarak hatayı birlikte çözebiliriz."
            ),
        )
        root.destroy()
    except Exception:
        print(details)


def run() -> None:
    try:
        from business_data_studio.app import main

        main()
    except Exception:
        details = traceback.format_exc()
        log_path = Path(__file__).resolve().parents[1] / "startup_error.log"
        try:
            log_path.write_text(details, encoding="utf-8")
        except OSError:
            pass
        _show_startup_error(details, log_path)


if __name__ == "__main__":
    run()
